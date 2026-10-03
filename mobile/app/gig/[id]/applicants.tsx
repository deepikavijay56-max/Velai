/**
 * app/gig/[id]/applicants.tsx
 * Poster view: list of applicants for a gig with accept button.
 */
import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  SafeAreaView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { appsApi, Application } from '@/lib/api';
import { ApplicantCard } from '@/components/ApplicantCard';
import { Colors, Spacing, Typography } from '@/constants/theme';

export default function ApplicantsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [acceptingId, setAcceptingId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const { data } = await appsApi.listForGig(id);
      setApplications(data);
    } catch {
      Alert.alert('Error', 'Could not load applicants.');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleAccept(appId: string) {
    Alert.alert('Accept applicant', 'This will start the gig and close other applications.', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Accept',
        onPress: async () => {
          setAcceptingId(appId);
          try {
            await appsApi.accept(appId);
            await load();
            Alert.alert('Accepted', 'The applicant has been accepted. Confirm the contract to begin.');
          } catch (err: any) {
            const msg = err?.response?.data?.detail ?? 'Could not accept. Try again.';
            Alert.alert('Error', typeof msg === 'string' ? msg : 'Error accepting.');
          } finally {
            setAcceptingId(null);
          }
        },
      },
    ]);
  }

  return (
    <SafeAreaView style={styles.safe}>
      <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
        <Text style={styles.backText}>← Back</Text>
      </TouchableOpacity>

      <View style={styles.header}>
        <Text style={styles.heading}>Applicants</Text>
        <Text style={styles.sub}>{applications.length} application{applications.length !== 1 ? 's' : ''}</Text>
      </View>

      {isLoading ? (
        <ActivityIndicator color={Colors.navy} style={{ marginTop: 40 }} size="large" />
      ) : (
        <FlatList
          data={applications}
          keyExtractor={(a) => a.id}
          renderItem={({ item }) => (
            <ApplicantCard
              application={item}
              onAccept={() => handleAccept(item.id)}
              isAccepting={acceptingId === item.id}
            />
          )}
          ListEmptyComponent={
            <View style={styles.empty}>
              <Text style={styles.emptyIcon}>📭</Text>
              <Text style={styles.emptyTitle}>No applications yet</Text>
              <Text style={styles.emptyBody}>Share your gig to attract applicants.</Text>
            </View>
          }
          contentContainerStyle={styles.list}
          onRefresh={load}
          refreshing={isLoading}
          showsVerticalScrollIndicator={false}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bgLight },
  backBtn: { paddingHorizontal: Spacing.base, paddingTop: Spacing.base },
  backText: { fontSize: Typography.size.base, color: Colors.navy, fontFamily: Typography.fontFamily.medium },
  header: { paddingHorizontal: Spacing.base, paddingTop: Spacing.sm, paddingBottom: Spacing.md },
  heading: { fontSize: Typography.size['2xl'], fontFamily: Typography.fontFamily.bold, color: Colors.textPrimary },
  sub: { fontSize: Typography.size.sm, color: Colors.textSecondary, fontFamily: Typography.fontFamily.regular, marginTop: 2 },
  list: { padding: Spacing.base, paddingBottom: 100 },
  empty: { alignItems: 'center', paddingTop: Spacing['3xl'], paddingHorizontal: Spacing.xl },
  emptyIcon: { fontSize: 48, marginBottom: Spacing.base },
  emptyTitle: { fontSize: Typography.size.lg, fontFamily: Typography.fontFamily.semiBold, color: Colors.textPrimary, marginBottom: Spacing.sm },
  emptyBody: { fontSize: Typography.size.base, color: Colors.textSecondary, textAlign: 'center', fontFamily: Typography.fontFamily.regular },
});
