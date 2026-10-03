/**
 * components/ApplicantCard.tsx
 * Card showing one application in the poster's applicants list.
 */
import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { Colors, Radii, Shadow, Spacing, Typography } from '../constants/theme';
import { Application } from '../lib/api';

interface Props {
  application: Application;
  onAccept?: () => void;
  isAccepting?: boolean;
}

const STATUS_STYLES: Record<string, { bg: string; text: string }> = {
  Pending: { bg: Colors.amberLight, text: '#92400E' },
  Accepted: { bg: Colors.greenLight, text: '#065F46' },
  Rejected: { bg: Colors.errorLight, text: '#991B1B' },
  Withdrawn: { bg: '#F3F4F6', text: '#6B7280' },
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { day: 'numeric', month: 'short' });
}

export function ApplicantCard({ application, onAccept, isAccepting }: Props) {
  const s = STATUS_STYLES[application.status] ?? STATUS_STYLES['Pending'];

  return (
    <View style={styles.card}>
      {/* Header */}
      <View style={styles.row}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>👤</Text>
        </View>
        <View style={styles.info}>
          <Text style={styles.label}>Applied {formatDate(application.created_at)}</Text>
          <View style={[styles.badge, { backgroundColor: s.bg }]}>
            <Text style={[styles.badgeText, { color: s.text }]}>{application.status}</Text>
          </View>
        </View>
      </View>

      {/* Pitch */}
      <Text style={styles.pitch} numberOfLines={4}>
        {application.pitch}
      </Text>

      {/* Pricing row */}
      <View style={[styles.row, styles.priceRow]}>
        <View style={styles.stat}>
          <Text style={styles.statLabel}>Proposed price</Text>
          <Text style={styles.statValue}>₹{application.proposed_price}</Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.statLabel}>Days needed</Text>
          <Text style={styles.statValue}>{application.proposed_days}d</Text>
        </View>
        {application.sample_url && (
          <View style={styles.stat}>
            <Text style={styles.statLabel}>Sample</Text>
            <Text style={[styles.statValue, { color: Colors.green }]}>View ↗</Text>
          </View>
        )}
      </View>

      {/* Accept button — only shown when pending and handler provided */}
      {application.status === 'Pending' && onAccept && (
        <TouchableOpacity
          style={[styles.acceptBtn, isAccepting && styles.acceptBtnDisabled]}
          onPress={onAccept}
          disabled={isAccepting}
          activeOpacity={0.85}
          accessibilityRole="button"
          accessibilityLabel="Accept this applicant"
        >
          <Text style={styles.acceptText}>{isAccepting ? 'Accepting…' : 'Accept applicant'}</Text>
        </TouchableOpacity>
      )}
    </View>
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
  avatar: {
    width: 40,
    height: 40,
    borderRadius: Radii.full,
    backgroundColor: Colors.bgLight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: { fontSize: 20 },
  info: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  label: {
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
    fontFamily: Typography.fontFamily.regular,
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
  pitch: {
    marginTop: Spacing.sm,
    fontSize: Typography.size.base,
    color: Colors.textPrimary,
    lineHeight: Typography.size.base * 1.6,
    fontFamily: Typography.fontFamily.regular,
  },
  priceRow: {
    marginTop: Spacing.md,
    paddingTop: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    justifyContent: 'space-around',
  },
  stat: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: Typography.size.xs,
    color: Colors.textMuted,
    fontFamily: Typography.fontFamily.regular,
  },
  statValue: {
    fontSize: Typography.size.md,
    fontFamily: Typography.fontFamily.bold,
    color: Colors.textPrimary,
    marginTop: 2,
  },
  acceptBtn: {
    marginTop: Spacing.md,
    backgroundColor: Colors.green,
    borderRadius: Radii.button,
    paddingVertical: 13,
    alignItems: 'center',
  },
  acceptBtnDisabled: {
    opacity: 0.6,
  },
  acceptText: {
    color: '#FFFFFF',
    fontSize: Typography.size.md,
    fontFamily: Typography.fontFamily.semiBold,
  },
});
