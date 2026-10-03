/**
 * components/RatingModal.tsx
 * Bottom-sheet style modal for leaving a rating after a gig completes.
 */
import React, { useState } from 'react';
import {
  Modal,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { Colors, Radii, Shadow, Spacing, Typography } from '../constants/theme';

interface Props {
  visible: boolean;
  onSubmit: (rating: number, text: string, tags: string[]) => void;
  onDismiss: () => void;
  isSubmitting?: boolean;
}

const TAGS = ['Fast delivery', 'Great quality', 'Easy to work with', 'Professional', 'Responsive'];
const STARS = [1, 2, 3, 4, 5];

export function RatingModal({ visible, onSubmit, onDismiss, isSubmitting }: Props) {
  const [rating, setRating] = useState(0);
  const [text, setText] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  const toggleTag = (tag: string) =>
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );

  const handleSubmit = () => {
    if (rating === 0) return;
    onSubmit(rating, text, selectedTags);
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onDismiss}
    >
      <View style={styles.overlay}>
        <View style={styles.sheet}>
          <View style={styles.handle} />

          <Text style={styles.title}>Rate this gig</Text>
          <Text style={styles.subtitle}>How was your experience?</Text>

          {/* Stars */}
          <View style={styles.stars}>
            {STARS.map((s) => (
              <TouchableOpacity
                key={s}
                onPress={() => setRating(s)}
                accessibilityRole="button"
                accessibilityLabel={`${s} stars`}
              >
                <Text style={[styles.star, s <= rating && styles.starActive]}>★</Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Tags */}
          <View style={styles.tags}>
            {TAGS.map((tag) => {
              const active = selectedTags.includes(tag);
              return (
                <TouchableOpacity
                  key={tag}
                  style={[styles.tag, active && styles.tagActive]}
                  onPress={() => toggleTag(tag)}
                  activeOpacity={0.8}
                >
                  <Text style={[styles.tagText, active && styles.tagTextActive]}>{tag}</Text>
                </TouchableOpacity>
              );
            })}
          </View>

          {/* Review text */}
          <TextInput
            style={styles.input}
            placeholder="Write a short review (optional)…"
            placeholderTextColor={Colors.textMuted}
            value={text}
            onChangeText={setText}
            multiline
            numberOfLines={3}
            maxLength={500}
          />

          <TouchableOpacity
            style={[styles.btn, (rating === 0 || isSubmitting) && styles.btnDisabled]}
            onPress={handleSubmit}
            disabled={rating === 0 || isSubmitting}
            activeOpacity={0.85}
          >
            <Text style={styles.btnText}>{isSubmitting ? 'Submitting…' : 'Submit rating'}</Text>
          </TouchableOpacity>

          <TouchableOpacity onPress={onDismiss} style={styles.cancel}>
            <Text style={styles.cancelText}>Not now</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: Colors.overlay,
    justifyContent: 'flex-end',
  },
  sheet: {
    backgroundColor: Colors.cardLight,
    borderTopLeftRadius: Radii.xl,
    borderTopRightRadius: Radii.xl,
    padding: Spacing.xl,
    paddingBottom: 40,
    ...Shadow.elevated,
  },
  handle: {
    width: 40,
    height: 4,
    backgroundColor: Colors.border,
    borderRadius: Radii.full,
    alignSelf: 'center',
    marginBottom: Spacing.lg,
  },
  title: {
    fontSize: Typography.size.xl,
    fontFamily: Typography.fontFamily.bold,
    color: Colors.textPrimary,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: Typography.size.base,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginTop: Spacing.xs,
    marginBottom: Spacing.lg,
    fontFamily: Typography.fontFamily.regular,
  },
  stars: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: Spacing.md,
    marginBottom: Spacing.lg,
  },
  star: {
    fontSize: 40,
    color: Colors.border,
  },
  starActive: {
    color: Colors.amber,
  },
  tags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.sm,
    marginBottom: Spacing.base,
  },
  tag: {
    paddingHorizontal: Spacing.md,
    paddingVertical: 7,
    borderRadius: Radii.full,
    borderWidth: 1,
    borderColor: Colors.border,
    backgroundColor: Colors.bgLight,
  },
  tagActive: {
    backgroundColor: Colors.navy,
    borderColor: Colors.navy,
  },
  tagText: {
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
    fontFamily: Typography.fontFamily.medium,
  },
  tagTextActive: {
    color: '#FFFFFF',
  },
  input: {
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: Radii.md,
    padding: Spacing.md,
    fontSize: Typography.size.base,
    color: Colors.textPrimary,
    fontFamily: Typography.fontFamily.regular,
    marginBottom: Spacing.base,
    minHeight: 80,
    textAlignVertical: 'top',
  },
  btn: {
    backgroundColor: Colors.green,
    borderRadius: Radii.button,
    paddingVertical: 14,
    alignItems: 'center',
  },
  btnDisabled: {
    opacity: 0.5,
  },
  btnText: {
    color: '#FFFFFF',
    fontFamily: Typography.fontFamily.semiBold,
    fontSize: Typography.size.md,
  },
  cancel: {
    alignItems: 'center',
    marginTop: Spacing.md,
  },
  cancelText: {
    fontSize: Typography.size.base,
    color: Colors.textSecondary,
    fontFamily: Typography.fontFamily.regular,
  },
});
