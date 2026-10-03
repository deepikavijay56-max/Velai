/**
 * app/(tabs)/me.tsx
 * Profile screen: name, department, year, reputation, skills, sign‑out.
 */
import React, { useState } from 'react';
import {
  Alert,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useAuth } from '@/hooks/useAuth';
import { Colors, Radii, Shadow, Spacing, Typography } from '@/constants/theme';

function SkillPill({ name, level }: { name: string; level: string }) {
  const levelColor =
    level === 'expert'
      ? Colors.amber
      : level === 'intermediate'
      ? Colors.green
      : Colors.textSecondary;
  return (
    <View style={styles.pill}>
      <Text style={styles.pillName}>{name}</Text>
      <Text style={[styles.pillLevel, { color: levelColor }]}>{level}</Text>
    </View>
  );
}

export default function MeScreen() {
  const { user, signOut } = useAuth();
  const [signingOut, setSigningOut] = useState(false);

  async function handleSignOut() {
    Alert.alert('Sign out', 'Are you sure?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Sign out',
        style: 'destructive',
        onPress: async () => {
          setSigningOut(true);
          await signOut();
        },
      },
    ]);
  }

  if (!user) return null;

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        {/* Avatar hero */}
        <View style={styles.hero}>
          <View style={styles.avatarCircle}>
            <Text style={styles.avatarInitial}>
              {user.name ? user.name[0].toUpperCase() : '?'}
            </Text>
          </View>
          <Text style={styles.name}>{user.name}</Text>
          <Text style={styles.email}>{user.email}</Text>
          <View style={styles.repRow}>
            <Text style={styles.repStar}>★</Text>
            <Text style={styles.repScore}>{user.reputation.toFixed(1)}</Text>
            <Text style={styles.repLabel}> reputation</Text>
          </View>
        </View>

        {/* Info card */}
        <View style={styles.card}>
          <Text style={styles.sectionLabel}>Profile</Text>
          <View style={styles.infoRow}>
            <Text style={styles.infoKey}>Department</Text>
            <Text style={styles.infoValue}>{user.department ?? '—'}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoKey}>Year</Text>
            <Text style={styles.infoValue}>{user.year ?? '—'}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoKey}>Role</Text>
            <Text style={styles.infoValue}>{user.role}</Text>
          </View>
        </View>

        {/* Skills placeholder */}
        <View style={styles.card}>
          <Text style={styles.sectionLabel}>Skills</Text>
          <Text style={styles.noSkills}>
            No skills added yet. Add skills to be matched with relevant gigs.
          </Text>
        </View>

        {/* Sign out */}
        <TouchableOpacity
          style={styles.signOutBtn}
          onPress={handleSignOut}
          disabled={signingOut}
          activeOpacity={0.85}
        >
          <Text style={styles.signOutText}>{signingOut ? 'Signing out…' : 'Sign out'}</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bgLight },
  scroll: { paddingBottom: 100 },
  hero: {
    alignItems: 'center',
    paddingTop: Spacing.xl,
    paddingBottom: Spacing.xl,
    backgroundColor: Colors.cardLight,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  avatarCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: Colors.navy,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.sm,
  },
  avatarInitial: {
    fontSize: Typography.size['2xl'],
    fontFamily: Typography.fontFamily.bold,
    color: '#FFFFFF',
  },
  name: {
    fontSize: Typography.size.xl,
    fontFamily: Typography.fontFamily.bold,
    color: Colors.textPrimary,
  },
  email: {
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
    marginTop: 4,
    fontFamily: Typography.fontFamily.regular,
  },
  repRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: Spacing.sm,
  },
  repStar: { fontSize: 18, color: Colors.amber },
  repScore: {
    fontSize: Typography.size.lg,
    fontFamily: Typography.fontFamily.bold,
    color: Colors.textPrimary,
    marginLeft: 4,
  },
  repLabel: {
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
    fontFamily: Typography.fontFamily.regular,
  },
  card: {
    backgroundColor: Colors.cardLight,
    marginHorizontal: Spacing.base,
    marginTop: Spacing.base,
    borderRadius: Radii.card,
    padding: Spacing.base,
    ...Shadow.card,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  sectionLabel: {
    fontSize: Typography.size.sm,
    fontFamily: Typography.fontFamily.semiBold,
    color: Colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: Spacing.sm,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  infoKey: {
    fontSize: Typography.size.base,
    color: Colors.textSecondary,
    fontFamily: Typography.fontFamily.regular,
  },
  infoValue: {
    fontSize: Typography.size.base,
    color: Colors.textPrimary,
    fontFamily: Typography.fontFamily.medium,
  },
  pill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.bgLight,
    borderRadius: Radii.full,
    paddingHorizontal: Spacing.md,
    paddingVertical: 6,
    marginRight: Spacing.sm,
    marginBottom: Spacing.sm,
    borderWidth: 1,
    borderColor: Colors.border,
    gap: 6,
  },
  pillName: {
    fontSize: Typography.size.sm,
    color: Colors.textPrimary,
    fontFamily: Typography.fontFamily.medium,
  },
  pillLevel: {
    fontSize: Typography.size.xs,
    fontFamily: Typography.fontFamily.semiBold,
  },
  noSkills: {
    fontSize: Typography.size.base,
    color: Colors.textSecondary,
    fontFamily: Typography.fontFamily.regular,
    lineHeight: Typography.size.base * 1.6,
  },
  signOutBtn: {
    marginHorizontal: Spacing.base,
    marginTop: Spacing.xl,
    borderRadius: Radii.button,
    borderWidth: 1.5,
    borderColor: Colors.error,
    paddingVertical: 13,
    alignItems: 'center',
  },
  signOutText: {
    color: Colors.error,
    fontSize: Typography.size.md,
    fontFamily: Typography.fontFamily.semiBold,
  },
});
