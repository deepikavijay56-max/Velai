/**
 * app/(tabs)/index.tsx
 * Gig feed with search + category filters. Paginated.
 */
import React, { useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { FilterBar } from '@/components/FilterBar';
import { GigCard } from '@/components/GigCard';
import { useGigFeed } from '@/hooks/useGigs';
import { Gig } from '@/lib/api';
import { Colors, Spacing, Typography } from '@/constants/theme';

export default function GigFeedScreen() {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');

  const filters = {
    search: search || undefined,
    category: category === 'All' ? undefined : category,
    status: 'Open' as const,
  };

  const { gigs, isLoading, isRefreshing, error, refresh, loadMore } = useGigFeed(filters);

  function renderItem({ item }: { item: Gig }) {
    return (
      <GigCard
        gig={item}
        onPress={() => router.push({ pathname: '/gig/[id]', params: { id: item.id } })}
      />
    );
  }

  function renderEmpty() {
    if (isLoading) return null;
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyIcon}>🔍</Text>
        <Text style={styles.emptyTitle}>No gigs yet</Text>
        <Text style={styles.emptyBody}>
          {search
            ? `No results for "${search}". Try a different search.`
            : 'No open gigs right now. Check back soon or post the first one.'}
        </Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Gigs</Text>
        <Text style={styles.subtitle}>Find campus work that fits your skills</Text>
      </View>

      <FilterBar
        search={search}
        onSearchChange={setSearch}
        selectedCategory={category}
        onCategoryChange={setCategory}
      />

      {/* Feed */}
      <FlatList
        data={gigs}
        keyExtractor={(g) => g.id}
        renderItem={renderItem}
        contentContainerStyle={styles.list}
        ListEmptyComponent={renderEmpty}
        ListFooterComponent={
          isLoading && gigs.length > 0 ? (
            <ActivityIndicator color={Colors.navy} style={{ marginVertical: 20 }} />
          ) : null
        }
        onRefresh={refresh}
        refreshing={isRefreshing}
        onEndReached={loadMore}
        onEndReachedThreshold={0.3}
        showsVerticalScrollIndicator={false}
      />

      {/* Error banner */}
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
  title: {
    fontSize: Typography.size['2xl'],
    fontFamily: Typography.fontFamily.bold,
    color: Colors.textPrimary,
  },
  subtitle: {
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
    marginTop: 2,
    fontFamily: Typography.fontFamily.regular,
  },
  list: {
    padding: Spacing.base,
    paddingBottom: 100,
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
