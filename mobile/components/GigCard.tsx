/**
 * components/GigCard.tsx
 * Compact card shown in the gig feed list.
 */
import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { Colors, Radii, Shadow, Spacing, Typography } from '../constants/theme';
import { Gig } from '../lib/api';

interface Props {
  gig: Gig;
  onPress: () => void;
}

const CATEGORY_ICONS: Record<string, string> = {
  Design: '🎨',
  Video: '🎬',
  Photo: '📸',
  Web: '💻',
  Data: '📊',
  Writing: '✍️',
  Tutoring: '📚',
  Event: '🎉',
  Other: '📌',
};

function StatusBadge({ status }: { status: string }) {
  const colors = Colors.status[status] ?? Colors.status['Draft'];
  return (
    <View style={[styles.badge, { backgroundColor: colors.bg }]}>
      <Text style={[styles.badgeText, { color: colors.text }]}>{status}</Text>
    </View>
  );
}

function formatBudget(min: number, max: number) {
  if (min === max) return `₹${min}`;
  return `₹${min}–₹${max}`;
}

function formatDeadline(iso: string) {
  const diff = Math.ceil(
    (new Date(iso).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  );
  if (diff < 0) return 'Expired';
  if (diff === 0) return 'Due today';
  if (diff === 1) return 'Due tomorrow';
  return `${diff}d left`;
}

export function GigCard({ gig, onPress }: Props) {
  const icon = CATEGORY_ICONS[gig.category] ?? '📌';
  const deadlineLabel = formatDeadline(gig.deadline);
  const isNear = deadlineLabel === 'Due today' || deadlineLabel === 'Due tomorrow';

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={onPress}
      activeOpacity={0.88}
      accessibilityRole="button"
      accessibilityLabel={`${gig.title}, ${gig.status}, ${formatBudget(gig.budget_min, gig.budget_max)}`}
    >
      {/* Header row */}
      <View style={styles.row}>
        <View style={styles.iconWrap}>
          <Text style={styles.iconText}>{icon}</Text>
        </View>
        <View style={styles.titleWrap}>
          <Text style={styles.title} numberOfLines={2}>
            {gig.title}
          </Text>
          <Text style={styles.category}>{gig.category}</Text>
        </View>
        <StatusBadge status={gig.status} />
      </View>

      {/* Description */}
      <Text style={styles.description} numberOfLines={2}>
        {gig.description}
      </Text>

      {/* Footer row */}
      <View style={[styles.row, styles.footer]}>
        <Text style={styles.budget}>{formatBudget(gig.budget_min, gig.budget_max)}</Text>
        <Text style={[styles.deadline, isNear && styles.deadlineNear]}>{deadlineLabel}</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.cardLight,
    borderRadius: Radii.card,
    padding: Spacing.base,
    marginBottom: Spacing.md,
    ...Shadow.card,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  iconWrap: {
    width: 44,
    height: 44,
    borderRadius: Radii.md,
    backgroundColor: Colors.bgLight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconText: {
    fontSize: 22,
  },
  titleWrap: {
    flex: 1,
  },
  title: {
    fontSize: Typography.size.md,
    fontFamily: Typography.fontFamily.semiBold,
    color: Colors.textPrimary,
    lineHeight: Typography.size.md * 1.3,
  },
  category: {
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  badge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: 3,
    borderRadius: Radii.full,
  },
  badgeText: {
    fontSize: Typography.size.xs,
    fontFamily: Typography.fontFamily.semiBold,
  },
  description: {
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
    marginTop: Spacing.sm,
    lineHeight: Typography.size.sm * 1.6,
  },
  footer: {
    marginTop: Spacing.sm,
    justifyContent: 'space-between',
  },
  budget: {
    fontSize: Typography.size.base,
    fontFamily: Typography.fontFamily.bold,
    color: Colors.green,
  },
  deadline: {
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
    fontFamily: Typography.fontFamily.medium,
  },
  deadlineNear: {
    color: Colors.amber,
  },
});
