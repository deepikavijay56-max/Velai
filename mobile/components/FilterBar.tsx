/**
 * components/FilterBar.tsx
 * Horizontal scrollable pill chips for category + status filters.
 */
import React from 'react';
import {
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { Colors, Radii, Spacing, Typography } from '../constants/theme';

export const GIG_CATEGORIES = [
  'All',
  'Design',
  'Video',
  'Photo',
  'Web',
  'Data',
  'Writing',
  'Tutoring',
  'Event',
  'Other',
];

interface Props {
  search: string;
  onSearchChange: (v: string) => void;
  selectedCategory: string;
  onCategoryChange: (c: string) => void;
}

export function FilterBar({ search, onSearchChange, selectedCategory, onCategoryChange }: Props) {
  return (
    <View style={styles.container}>
      {/* Search */}
      <View style={styles.searchWrap}>
        <Text style={styles.searchIcon}>🔍</Text>
        <TextInput
          style={styles.searchInput}
          placeholder="Search gigs…"
          placeholderTextColor={Colors.textMuted}
          value={search}
          onChangeText={onSearchChange}
          returnKeyType="search"
          clearButtonMode="while-editing"
          accessibilityLabel="Search gigs"
        />
      </View>

      {/* Category chips */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.chips}
        keyboardShouldPersistTaps="handled"
      >
        {GIG_CATEGORIES.map((cat) => {
          const active = cat === selectedCategory;
          return (
            <TouchableOpacity
              key={cat}
              onPress={() => onCategoryChange(cat)}
              style={[styles.chip, active && styles.chipActive]}
              activeOpacity={0.8}
              accessibilityRole="button"
              accessibilityState={{ selected: active }}
            >
              <Text style={[styles.chipText, active && styles.chipTextActive]}>{cat}</Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.cardLight,
    paddingTop: Spacing.sm,
    paddingBottom: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  searchWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: Spacing.base,
    marginBottom: Spacing.sm,
    backgroundColor: Colors.bgLight,
    borderRadius: Radii.md,
    paddingHorizontal: Spacing.md,
    height: 44,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  searchIcon: {
    fontSize: 16,
    marginRight: Spacing.sm,
  },
  searchInput: {
    flex: 1,
    fontSize: Typography.size.base,
    color: Colors.textPrimary,
    fontFamily: Typography.fontFamily.regular,
  },
  chips: {
    paddingHorizontal: Spacing.base,
    gap: Spacing.sm,
    flexDirection: 'row',
  },
  chip: {
    paddingHorizontal: Spacing.md,
    paddingVertical: 7,
    borderRadius: Radii.full,
    backgroundColor: Colors.bgLight,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  chipActive: {
    backgroundColor: Colors.navy,
    borderColor: Colors.navy,
  },
  chipText: {
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
    fontFamily: Typography.fontFamily.medium,
  },
  chipTextActive: {
    color: '#FFFFFF',
  },
});
