/**
 * app/gig/[id]/index.tsx
 * Gig detail page: shows full info, and lets a student apply.
 */
import React, { useState } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { useGig } from '@/hooks/useGigs';
import { useAuth } from '@/hooks/useAuth';
import { appsApi } from '@/lib/api';
import { Colors, Radii, Shadow, Spacing, Typography } from '@/constants/theme';

export default function GigDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { gig, isLoading, error } = useGig(id);
  const { user } = useAuth();

  const [showApply, setShowApply] = useState(false);
  const [pitch, setPitch] = useState('');
  const [proposedPrice, setProposedPrice] = useState('');
  const [proposedDays, setProposedDays] = useState('');
  const [sampleUrl, setSampleUrl] = useState('');
  const [isApplying, setIsApplying] = useState(false);

  async function handleApply() {
    if (!pitch.trim() || !proposedPrice || !proposedDays) {
      Alert.alert('Missing fields', 'Fill in your pitch, price, and estimated days.');
      return;
    }
    setIsApplying(true);
    try {
      await appsApi.apply(id, {
        pitch: pitch.trim(),
        proposed_price: Number(proposedPrice),
        proposed_days: Number(proposedDays),
        sample_url: sampleUrl.trim() || undefined,
      });
      Alert.alert('Applied!', 'Your application was submitted.');
      setShowApply(false);
      router.back();
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? 'Could not submit. Try again.';
      Alert.alert('Error', typeof msg === 'string' ? msg : 'Could not submit.');
    } finally {
      setIsApplying(false);
    }
  }

  if (isLoading) {
    return (
      <SafeAreaView style={styles.safe}>
        <Text style={styles.loading}>Loading…</Text>
      </SafeAreaView>
    );
  }

  if (error || !gig) {
    return (
      <SafeAreaView style={styles.safe}>
        <Text style={styles.errMsg}>{error ?? 'Gig not found.'}</Text>
      </SafeAreaView>
    );
  }

  const isOwner = gig.poster_id === user?.id;
  const statusColors = Colors.status[gig.status] ?? { bg: '#F3F4F6', text: '#6B7280' };
  const canApply = gig.status === 'Open' && !isOwner;

  return (
    <KeyboardAvoidingView
      style={styles.safe}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <SafeAreaView style={styles.safe}>
        {/* Back */}
        <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>

        <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
          {/* Status badge */}
          <View style={[styles.badge, { backgroundColor: statusColors.bg }]}>
            <Text style={[styles.badgeText, { color: statusColors.text }]}>{gig.status}</Text>
          </View>

          <Text style={styles.title}>{gig.title}</Text>
          <Text style={styles.category}>{gig.category}</Text>

          {/* Budget + deadline */}
          <View style={styles.metaRow}>
            <View style={styles.metaItem}>
              <Text style={styles.metaLabel}>Budget</Text>
              <Text style={styles.metaValue}>₹{gig.budget_min}–₹{gig.budget_max}</Text>
            </View>
            <View style={styles.metaItem}>
              <Text style={styles.metaLabel}>Deadline</Text>
              <Text style={styles.metaValue}>
                {new Date(gig.deadline).toLocaleDateString()}
              </Text>
            </View>
            <View style={styles.metaItem}>
              <Text style={styles.metaLabel}>Revisions</Text>
              <Text style={styles.metaValue}>{gig.revisions}</Text>
            </View>
          </View>

          {/* Description */}
          <View style={styles.section}>
            <Text style={styles.sectionLabel}>Description</Text>
            <Text style={styles.description}>{gig.description}</Text>
          </View>

          {/* Poster actions */}
          {isOwner && gig.status === 'Open' && (
            <TouchableOpacity
              style={styles.applicantsBtn}
              onPress={() =>
                router.push({ pathname: '/gig/[id]/applicants', params: { id: gig.id } })
              }
            >
              <Text style={styles.applicantsBtnText}>View applicants</Text>
            </TouchableOpacity>
          )}

          {/* Apply form */}
          {canApply && !showApply && (
            <TouchableOpacity style={styles.applyBtn} onPress={() => setShowApply(true)}>
              <Text style={styles.applyBtnText}>Apply for this gig</Text>
            </TouchableOpacity>
          )}

          {canApply && showApply && (
            <View style={styles.applyCard}>
              <Text style={styles.applyTitle}>Your application</Text>

              <Text style={styles.fieldLabel}>Pitch *</Text>
              <TextInput
                style={[styles.input, styles.multiline]}
                placeholder="Describe why you're the right fit…"
                placeholderTextColor={Colors.textMuted}
                multiline
                numberOfLines={4}
                value={pitch}
                onChangeText={setPitch}
              />

              <View style={styles.row}>
                <View style={styles.half}>
                  <Text style={styles.fieldLabel}>Proposed price (₹) *</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="e.g. 1500"
                    placeholderTextColor={Colors.textMuted}
                    keyboardType="numeric"
                    value={proposedPrice}
                    onChangeText={setProposedPrice}
                  />
                </View>
                <View style={styles.half}>
                  <Text style={styles.fieldLabel}>Days needed *</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="e.g. 3"
                    placeholderTextColor={Colors.textMuted}
                    keyboardType="numeric"
                    value={proposedDays}
                    onChangeText={setProposedDays}
                  />
                </View>
              </View>

              <Text style={styles.fieldLabel}>Sample link (optional)</Text>
              <TextInput
                style={styles.input}
                placeholder="https://…"
                placeholderTextColor={Colors.textMuted}
                keyboardType="url"
                autoCapitalize="none"
                value={sampleUrl}
                onChangeText={setSampleUrl}
              />

              <TouchableOpacity
                style={[styles.applyBtn, isApplying && styles.btnDisabled]}
                onPress={handleApply}
                disabled={isApplying}
              >
                <Text style={styles.applyBtnText}>{isApplying ? 'Applying…' : 'Submit application'}</Text>
              </TouchableOpacity>

              <TouchableOpacity onPress={() => setShowApply(false)} style={styles.cancelLink}>
                <Text style={styles.cancelText}>Cancel</Text>
              </TouchableOpacity>
            </View>
          )}
        </ScrollView>
      </SafeAreaView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bgLight },
  loading: { textAlign: 'center', marginTop: 60, color: Colors.textSecondary },
  errMsg: { textAlign: 'center', marginTop: 60, color: Colors.error },
  backBtn: { paddingHorizontal: Spacing.base, paddingTop: Spacing.base, paddingBottom: Spacing.sm },
  backText: { fontSize: Typography.size.base, color: Colors.navy, fontFamily: Typography.fontFamily.medium },
  scroll: { padding: Spacing.base, paddingBottom: 120 },
  badge: { alignSelf: 'flex-start', paddingHorizontal: Spacing.sm, paddingVertical: 4, borderRadius: Radii.full, marginBottom: Spacing.sm },
  badgeText: { fontSize: Typography.size.xs, fontFamily: Typography.fontFamily.semiBold },
  title: { fontSize: Typography.size['2xl'], fontFamily: Typography.fontFamily.bold, color: Colors.textPrimary, lineHeight: Typography.size['2xl'] * 1.25 },
  category: { fontSize: Typography.size.sm, color: Colors.textSecondary, marginTop: 4, marginBottom: Spacing.base, fontFamily: Typography.fontFamily.regular },
  metaRow: { flexDirection: 'row', backgroundColor: Colors.cardLight, borderRadius: Radii.card, padding: Spacing.base, marginBottom: Spacing.base, ...Shadow.card, borderWidth: 1, borderColor: Colors.border },
  metaItem: { flex: 1, alignItems: 'center' },
  metaLabel: { fontSize: Typography.size.xs, color: Colors.textMuted, fontFamily: Typography.fontFamily.regular, marginBottom: 4 },
  metaValue: { fontSize: Typography.size.md, fontFamily: Typography.fontFamily.bold, color: Colors.textPrimary },
  section: { backgroundColor: Colors.cardLight, borderRadius: Radii.card, padding: Spacing.base, marginBottom: Spacing.base, ...Shadow.card, borderWidth: 1, borderColor: Colors.border },
  sectionLabel: { fontSize: Typography.size.sm, fontFamily: Typography.fontFamily.semiBold, color: Colors.textSecondary, textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: Spacing.sm },
  description: { fontSize: Typography.size.base, color: Colors.textPrimary, lineHeight: Typography.size.base * 1.7, fontFamily: Typography.fontFamily.regular },
  applicantsBtn: { backgroundColor: Colors.navy, borderRadius: Radii.button, paddingVertical: 14, alignItems: 'center', marginBottom: Spacing.md },
  applicantsBtnText: { color: '#FFFFFF', fontSize: Typography.size.md, fontFamily: Typography.fontFamily.semiBold },
  applyBtn: { backgroundColor: Colors.green, borderRadius: Radii.button, paddingVertical: 14, alignItems: 'center', marginBottom: Spacing.sm },
  btnDisabled: { opacity: 0.5 },
  applyBtnText: { color: '#FFFFFF', fontSize: Typography.size.md, fontFamily: Typography.fontFamily.semiBold },
  applyCard: { backgroundColor: Colors.cardLight, borderRadius: Radii.card, padding: Spacing.base, marginTop: Spacing.sm, ...Shadow.card, borderWidth: 1, borderColor: Colors.border },
  applyTitle: { fontSize: Typography.size.lg, fontFamily: Typography.fontFamily.bold, color: Colors.textPrimary, marginBottom: Spacing.base },
  fieldLabel: { fontSize: Typography.size.sm, color: Colors.textSecondary, fontFamily: Typography.fontFamily.medium, marginBottom: Spacing.xs, marginTop: Spacing.sm },
  input: { backgroundColor: Colors.bgLight, borderRadius: Radii.md, borderWidth: 1, borderColor: Colors.border, paddingHorizontal: Spacing.base, height: 48, fontSize: Typography.size.base, color: Colors.textPrimary, fontFamily: Typography.fontFamily.regular },
  multiline: { height: 100, textAlignVertical: 'top', paddingTop: Spacing.sm },
  row: { flexDirection: 'row', gap: Spacing.sm },
  half: { flex: 1 },
  cancelLink: { alignItems: 'center', marginTop: Spacing.sm },
  cancelText: { color: Colors.textSecondary, fontSize: Typography.size.base, fontFamily: Typography.fontFamily.regular },
});
