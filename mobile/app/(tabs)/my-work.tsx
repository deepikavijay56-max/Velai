/**
 * app/(tabs)/my-work.tsx
 * List of gigs the user posted, plus gigs they are actively working on.
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
import { useAuth } from '@/hooks/useAuth';
import { contractsApi, Contract, gigsApi, Gig } from '@/lib/api';
import { Colors, Radii, Shadow, Spacing, Typography } from '@/constants/theme';

export default function MyWorkScreen() {
  const { user } = useAuth();
  const [gigs, setGigs] = useState<Gig[]>([]);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [{ data }, { data: myContracts }] = await Promise.all([
        gigsApi.list({ page_size: 50 }),
        contractsApi.listMine(),
      ]);
      // Filter to gigs the current user posted
      const mine = data.filter((g) => g.poster_id === user?.id);
      setGigs(mine);
      setContracts(myContracts);
    } catch {
      setError('Could not load your gigs. Pull to retry.');
    } finally {
      setIsLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    load();
  }, [load]);

  function renderItem({ item }: { item: Gig }) {
    const statusColors =
      Colors.status[item.status] ?? { bg: '#F3F4F6', text: '#6B7280' };
    return (
      <TouchableOpacity
        style={styles.card}
        onPress={() =>
          router.push({ pathname: '/gig/[id]', params: { id: item.id } })
        }
        activeOpacity={0.88}
      >
        <View style={styles.rowBetween}>
          <Text style={styles.cardTitle} numberOfLines={2}>
            {item.title}
          </Text>
          <View style={[styles.badge, { backgroundColor: statusColors.bg }]}>
            <Text style={[styles.badgeText, { color: statusColors.text }]}>
              {item.status}
            </Text>
          </View>
        </View>
        <Text style={styles.category}>{item.category}</Text>
        <View style={styles.rowBetween}>
          <Text style={styles.budget}>
            ₹{item.budget_min}–₹{item.budget_max}
          </Text>
          <Text style={styles.deadline}>
            Due {new Date(item.deadline).toLocaleDateString()}
          </Text>
        </View>
      </TouchableOpacity>
    );
  }

  function renderEmpty() {
    if (isLoading || contracts.length > 0) return null;
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyIcon}>💼</Text>
        <Text style={styles.emptyTitle}>No gigs yet</Text>
        <Text style={styles.emptyBody}>
          Post your first gig and it will appear here.
        </Text>
        <TouchableOpacity
          style={styles.postBtn}
          onPress={() => router.push('/(tabs)/post')}
        >
          <Text style={styles.postBtnText}>Post a gig</Text>
        </TouchableOpacity>
      </View>
    );
  }

  function renderContracts() {
    if (contracts.length === 0) return null;
    return (
      <View style={styles.contractSection}>
        <Text style={styles.contractHeading}>Accepted gigs</Text>
        {contracts.map((contract) => {
          const statusColors =
            contract.gig
              ? Colors.status[contract.gig.status]
              : { bg: '#F3F4F6', text: '#6B7280' };
          return (
            <TouchableOpacity
              key={contract.id}
              style={styles.card}
              onPress={() =>
                router.push({
                  pathname: '/gig/[id]/workspace',
                  params: { id: contract.gig_id },
                })
              }
              activeOpacity={0.88}
            >
              <View style={styles.rowBetween}>
                <Text style={styles.cardTitle} numberOfLines={2}>
                  {contract.gig?.title ?? 'Gig workspace'}
                </Text>
                <View style={[styles.badge, { backgroundColor: statusColors.bg }]}>
                  <Text style={[styles.badgeText, { color: statusColors.text }]}>
                    {contract.status.replace('_', ' ')}
                  </Text>
                </View>
              </View>
              <Text style={styles.category}>Open workspace</Text>
            </TouchableOpacity>
          );
        })}
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.heading}>My work</Text>
        <Text style={styles.subheading}>Gigs you posted or are working on</Text>
      </View>

      {isLoading ? (
        <ActivityIndicator
          color={Colors.navy}
          style={{ marginTop: 40 }}
          size="large"
        />
      ) : (
        <FlatList
          data={gigs}
          keyExtractor={(g) => g.id}
          renderItem={renderItem}
          ListEmptyComponent={renderEmpty}
          ListHeaderComponent={renderContracts}
          contentContainerStyle={styles.list}
          onRefresh={load}
          refreshing={isLoading}
          showsVerticalScrollIndicator={false}
        />
      )}

      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: Colors.bgLight,
  },
  header: {
    paddingHorizontal: Spacing.base,
    paddingTop: Spacing.lg,
    paddingBottom: Spacing.sm,
    backgroundColor: Colors.cardLight,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  contractSection: { paddingHorizontal: Spacing.base, paddingTop: Spacing.base },
  contractHeading: {
    fontSize: Typography.size.lg,
    fontFamily: Typography.fontFamily.semiBold,
    color: Colors.textPrimary,
    marginBottom: Spacing.sm,
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
  list: {
    padding: Spacing.base,
    paddingBottom: 100,
  },
  card: {
    backgroundColor: Colors.cardLight,
    borderRadius: Radii.card,
    padding: Spacing.base,
    marginBottom: Spacing.md,
    ...Shadow.card,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  rowBetween: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  cardTitle: {
    flex: 1,
    fontSize: Typography.size.md,
    fontFamily: Typography.fontFamily.semiBold,
    color: Colors.textPrimary,
  },
  badge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: 3,
    borderRadius: Radii.full,
    flexShrink: 0,
  },
  badgeText: {
    fontSize: Typography.size.xs,
    fontFamily: Typography.fontFamily.semiBold,
  },
  category: {
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
    marginTop: 4,
    marginBottom: Spacing.sm,
    fontFamily: Typography.fontFamily.regular,
  },
  budget: {
    fontSize: Typography.size.base,
    fontFamily: Typography.fontFamily.bold,
    color: Colors.green,
  },
  deadline: {
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
    fontFamily: Typography.fontFamily.regular,
  },
  empty: {
    alignItems: 'center',
    paddingTop: Spacing['3xl'],
    paddingHorizontal: Spacing.xl,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: Spacing.base,
  },
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
    marginBottom: Spacing.xl,
  },
  postBtn: {
    backgroundColor: Colors.green,
    borderRadius: Radii.button,
    paddingHorizontal: Spacing.xl,
    paddingVertical: 13,
  },
  postBtnText: {
    color: '#FFFFFF',
    fontSize: Typography.size.md,
    fontFamily: Typography.fontFamily.semiBold,
  },
  errorBanner: {
    position: 'absolute',
    bottom: 90,
    left: Spacing.base,
    right: Spacing.base,
    backgroundColor: Colors.errorLight,
    borderRadius: 10,
    padding: Spacing.md,
  },
  errorText: {
    color: Colors.error,
    textAlign: 'center',
    fontSize: Typography.size.sm,
    fontFamily: Typography.fontFamily.medium,
  },
});
