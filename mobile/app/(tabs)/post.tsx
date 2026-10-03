/**
 * app/(tabs)/post.tsx
 * Form for posting a new gig (Phase‑1 fields only).
 */
import React, { useState } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { gigsApi, CreateGigPayload, Gig } from '@/lib/api';
import { Colors, Radii, Spacing, Typography } from '@/constants/theme';

export default function PostGigScreen() {
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [budgetMin, setBudgetMin] = useState('');
  const [budgetMax, setBudgetMax] = useState('');
  const [deadline, setDeadline] = useState(''); // yyyy-mm-dd
  const [revisions, setRevisions] = useState('1');
  const [description, setDescription] = useState('');
  const [deliverablesText, setDeliverablesText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit() {
    const deliverables = deliverablesText
      .split(/[\n,]/)
      .map((deliverable) => deliverable.trim())
      .filter(Boolean);
    if (
      title.trim().length < 5 ||
      category.trim().length < 2 ||
      description.trim().length < 15 ||
      !budgetMin ||
      !budgetMax ||
      !deadline ||
      deliverables.length === 0
    ) {
      Alert.alert('Missing fields', 'Please fill out all required fields.');
      return;
    }
    const payload: CreateGigPayload = {
      title: title.trim(),
      description: description.trim(),
      category: category.trim(),
      deliverables,
      budget_min: Number(budgetMin),
      budget_max: Number(budgetMax),
      deadline,
      revisions: Number(revisions),
    };
    setIsSubmitting(true);
    try {
      const { data } = await gigsApi.create(payload);
      // navigate to the new gig detail page
      router.replace({ pathname: '/gig/[id]', params: { id: data.id } });
    } catch (err) {
      Alert.alert('Error', 'Could not post the gig. Try again later.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>Post a Gig</Text>
        <Text style={styles.sub}>All fields are required for Phase 1.</Text>

        <TextInput
          style={styles.input}
          placeholder="Title (max 80 chars)"
          placeholderTextColor={Colors.textMuted}
          value={title}
          onChangeText={setTitle}
        />
        <TextInput
          style={styles.input}
          placeholder="Category (e.g. Design, Video)"
          placeholderTextColor={Colors.textMuted}
          value={category}
          onChangeText={setCategory}
        />
        <View style={styles.row}>
          <TextInput
            style={[styles.input, styles.half]}
            placeholder="Min budget"
            placeholderTextColor={Colors.textMuted}
            keyboardType="numeric"
            value={budgetMin}
            onChangeText={setBudgetMin}
          />
          <TextInput
            style={[styles.input, styles.half]}
            placeholder="Max budget"
            placeholderTextColor={Colors.textMuted}
            keyboardType="numeric"
            value={budgetMax}
            onChangeText={setBudgetMax}
          />
        </View>
        <TextInput
          style={styles.input}
          placeholder="Deadline (YYYY‑MM‑DD)"
          placeholderTextColor={Colors.textMuted}
          value={deadline}
          onChangeText={setDeadline}
        />
        <TextInput
          style={styles.input}
          placeholder="Revisions allowed (1‑5)"
          placeholderTextColor={Colors.textMuted}
          keyboardType="numeric"
          value={revisions}
          onChangeText={setRevisions}
        />
        <TextInput
          style={[styles.input, styles.multiline]}
          placeholder="Description"
          placeholderTextColor={Colors.textMuted}
          multiline
          numberOfLines={4}
          value={description}
          onChangeText={setDescription}
        />
        <TextInput
          style={[styles.input, styles.multiline]}
          placeholder="Deliverables (one per line or comma-separated)"
          placeholderTextColor={Colors.textMuted}
          multiline
          numberOfLines={3}
          value={deliverablesText}
          onChangeText={setDeliverablesText}
        />

        <TouchableOpacity
          style={[styles.btn, isSubmitting && styles.btnDisabled]}
          onPress={handleSubmit}
          disabled={isSubmitting}
        >
          <Text style={styles.btnText}>{isSubmitting ? 'Posting…' : 'Post gig'}</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.bgLight },
  scroll: { padding: Spacing.xl },
  title: {
    fontSize: Typography.size['2xl'],
    fontFamily: Typography.fontFamily.bold,
    color: Colors.textPrimary,
    marginBottom: Spacing.sm,
  },
  sub: {
    fontSize: Typography.size.base,
    color: Colors.textSecondary,
    marginBottom: Spacing.md,
    fontFamily: Typography.fontFamily.regular,
  },
  input: {
    backgroundColor: Colors.cardLight,
    borderRadius: Radii.md,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingHorizontal: Spacing.base,
    height: 52,
    fontSize: Typography.size.base,
    color: Colors.textPrimary,
    marginBottom: Spacing.base,
    fontFamily: Typography.fontFamily.regular,
  },
  multiline: { height: 120, textAlignVertical: 'top' },
  row: { flexDirection: 'row', gap: Spacing.sm },
  half: { flex: 1 },
  btn: {
    backgroundColor: Colors.green,
    borderRadius: Radii.button,
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: Spacing.md,
  },
  btnDisabled: { opacity: 0.5 },
  btnText: {
    color: '#FFFFFF',
    fontSize: Typography.size.md,
    fontFamily: Typography.fontFamily.semiBold,
  },
});
