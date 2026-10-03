/**
 * app/(tabs)/chats.tsx
 * List of gig workspaces the user has active chat in.
 */
import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  SafeAreaView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { contractsApi, Contract } from '@/lib/api';
import { Colors, Radii, Shadow, Spacing, Typography } from '@/constants/theme';

export default function ChatsScreen() {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const { data } = await contractsApi.listMine();
      setContracts(data.filter((contract) => contract.status !== 'completed'));
    } catch {
      setError('Could not load your workspaces. Pull to retry.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  function renderItem({ item }: { item: Contract }) {
    return (
      <TouchableOpacity
        style={styles.card}
        onPress={() =>
          router.push({ pathname: '/gig/[id]/workspace', params: { id: item.gig_id } })
        }
        activeOpacity={0.88}
      >
        <View style={styles.row}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>💬</Text>
          </View>
          <View style={styles.info}>
            <Text style={styles.title} numberOfLines={1}>
              {item.gig?.title ?? 'Gig workspace'}
            </Text>
            <Text style={styles.sub}>Tap to open workspace</Text>
          </View>
          <Text style={styles.arrow}>›</Text>
        </View>
      </TouchableOpacity>
    );
  }

  function renderEmpty() {
    if (isLoading) return null;
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyIcon}>💬</Text>
        <Text style={styles.emptyTitle}>{error ? 'Workspaces unavailable' : 'No active chats'}</Text>
        <Text style={styles.emptyBody}>
          {error ?? 'Once a gig is accepted, the chat workspace will appear here.'}
        </Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.header}>
        <Text style={styles.heading}>Chats</Text>
        <Text style={styles.subheading}>Your active gig workspaces</Text>
      </View>

      {isLoading ? (
        <ActivityIndicator color={Colors.navy} style={{ marginTop: 40 }} size="large" />
      ) : (
        <FlatList
          data={contracts}
          keyExtractor={(contract) => contract.id}
          renderItem={renderItem}
          ListEmptyComponent={renderEmpty}
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
  header: {
    paddingHorizontal: Spacing.base,
    paddingTop: Spacing.lg,
    paddingBottom: Spacing.sm,
    backgroundColor: Colors.cardLight,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  heading: {
    fontSize: Typography.size['2xl'],
    fontFamily: Typography.fontFamily.bold,
    color: Colors.textPrimary,
  },
  subheading: {
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
    marginTop: 2,
    fontFamily: Typography.fontFamily.regular,
  },
  list: { padding: Spacing.base, paddingBottom: 100 },
  card: {
    backgroundColor: Colors.cardLight,
    borderRadius: Radii.card,
    padding: Spacing.base,
    marginBottom: Spacing.sm,
    ...Shadow.card,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  row: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: Radii.full,
    backgroundColor: Colors.bgLight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: { fontSize: 22 },
  info: { flex: 1 },
  title: {
    fontSize: Typography.size.md,
    fontFamily: Typography.fontFamily.semiBold,
    color: Colors.textPrimary,
  },
  sub: {
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
    marginTop: 2,
    fontFamily: Typography.fontFamily.regular,
  },
  arrow: { fontSize: 22, color: Colors.textMuted },
  empty: {
    alignItems: 'center',
    paddingTop: Spacing['3xl'],
    paddingHorizontal: Spacing.xl,
  },
  emptyIcon: { fontSize: 48, marginBottom: Spacing.base },
  emptyTitle: {
    fontSize: Typography.size.lg,
    fontFamily: Typography.fontFamily.semiBold,
    color: Colors.textPrimary,
    marginBottom: Spacing.sm,
  },
  emptyBody: {
    fontSize: Typography.size.base,
    color: Colors.textSecondary,
    textAlign: 'center',
    lineHeight: Typography.size.base * 1.6,
    fontFamily: Typography.fontFamily.regular,
  },
});
