/**
 * app/(auth)/verify.tsx
 * OTP verification + first-time onboarding (name, department, year, skills).
 */
import React, { useRef, useState } from 'react';
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
import { router, useLocalSearchParams } from 'expo-router';
import { useAuth } from '@/hooks/useAuth';
import { authApi, type UserSkillPayload } from '@/lib/api';
import { Colors, Radii, Spacing, Typography } from '@/constants/theme';

type Step = 'otp' | 'profile';
type AvailabilityStatus = 'available' | 'limited' | 'unavailable';

const SKILL_LEVELS: UserSkillPayload['level'][] = ['beginner', 'intermediate', 'expert'];
const AVAILABILITY_STATUSES: AvailabilityStatus[] = ['available', 'limited', 'unavailable'];

export default function VerifyScreen() {
  const { email } = useLocalSearchParams<{ email: string }>();
  const { signIn, refreshUser, user } = useAuth();

  const [step, setStep] = useState<Step>('otp');
  const [otpCode, setOtpCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Profile fields
  const [name, setName] = useState('');
  const [department, setDepartment] = useState('');
  const [year, setYear] = useState('');
  const [skills, setSkills] = useState<UserSkillPayload[]>([]);
  const [skillName, setSkillName] = useState('');
  const [skillLevel, setSkillLevel] = useState<UserSkillPayload['level']>('intermediate');
  const [sampleLinks, setSampleLinks] = useState('');
  const [availabilityStatus, setAvailabilityStatus] = useState<AvailabilityStatus>('available');
  const [hoursPerWeek, setHoursPerWeek] = useState('10');

  function handleAddSkill() {
    if (!skillName.trim()) {
      Alert.alert('Skill required', 'Enter a skill before adding it.');
      return;
    }

    const links = sampleLinks
      .split(/[\n,]/)
      .map((link) => link.trim())
      .filter(Boolean);
    if (links.length > 3) {
      Alert.alert('Too many links', 'Add up to 3 sample links per skill.');
      return;
    }

    setSkills((current) => [
      ...current,
      { skill_name: skillName.trim(), level: skillLevel, sample_links: links },
    ]);
    setSkillName('');
    setSampleLinks('');
    setSkillLevel('intermediate');
  }

  /* ── Step 1: Verify OTP ── */
  async function handleVerify() {
    if (otpCode.length !== 6) {
      Alert.alert('Invalid OTP', 'Enter the 6-digit code from your email.');
      return;
    }
    setIsLoading(true);
    try {
      await signIn(email, otpCode);
      // If profile is already complete, go to tabs
      // Otherwise show onboarding step
      setStep('profile');
    } catch {
      Alert.alert('Wrong code', 'That OTP is incorrect or expired. Try again.');
    } finally {
      setIsLoading(false);
    }
  }

  /* ── Step 2: Save profile ── */
  async function handleSaveProfile() {
    if (!name.trim()) {
      Alert.alert('Name required', 'Enter your full name.');
      return;
    }
    const parsedYear = year ? Number(year) : null;
    if (parsedYear !== null && (parsedYear < 1 || parsedYear > 4)) {
      Alert.alert('Invalid year', 'Enter a year from 1 to 4.');
      return;
    }
    if (skills.length === 0) {
      Alert.alert('Add a skill', 'Add at least one skill to your profile.');
      return;
    }
    const weeklyHours = Number(hoursPerWeek);
    if (!hoursPerWeek || !Number.isInteger(weeklyHours) || weeklyHours < 0 || weeklyHours > 168) {
      Alert.alert('Invalid availability', 'Enter between 0 and 168 available hours per week.');
      return;
    }
    setIsLoading(true);
    try {
      await authApi.updateMe({
        name: name.trim(),
        department: department.trim() || null,
        year: parsedYear,
        availability: { status: availabilityStatus, hours_per_week: weeklyHours },
      });
      await authApi.updateSkills(skills);
      await refreshUser();
      router.replace('/(tabs)');
    } catch {
      Alert.alert('Error', 'Could not save your profile. Try again.');
    } finally {
      setIsLoading(false);
    }
  }

  /* ── OTP input ── */
  if (step === 'otp') {
    return (
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <TouchableOpacity style={styles.back} onPress={() => router.back()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>

        <View style={styles.hero}>
          <Text style={styles.logo}>📬</Text>
          <Text style={styles.heading}>Check your email</Text>
          <Text style={styles.subText}>
            We sent a 6-digit code to{'\n'}
            <Text style={styles.emailText}>{email}</Text>
          </Text>
        </View>

        <View style={styles.card}>
          <TextInput
            style={styles.otpInput}
            placeholder="000000"
            placeholderTextColor={Colors.textMuted}
            value={otpCode}
            onChangeText={(v) => setOtpCode(v.replace(/\D/g, '').slice(0, 6))}
            keyboardType="number-pad"
            maxLength={6}
            returnKeyType="done"
            onSubmitEditing={handleVerify}
            textContentType="oneTimeCode"
            accessibilityLabel="One-time password"
          />

          <TouchableOpacity
            style={[styles.btn, (isLoading || otpCode.length !== 6) && styles.btnDisabled]}
            onPress={handleVerify}
            disabled={isLoading || otpCode.length !== 6}
            activeOpacity={0.85}
          >
            <Text style={styles.btnText}>{isLoading ? 'Verifying…' : 'Verify OTP'}</Text>
          </TouchableOpacity>

          <Text style={styles.hint}>
            Didn't get it? Check spam, or{' '}
            <Text
              style={styles.link}
              onPress={async () => {
                await authApi.requestOtp(email);
                Alert.alert('Sent', 'A new OTP has been sent.');
              }}
            >
              resend
            </Text>
            .
          </Text>
        </View>
      </KeyboardAvoidingView>
    );
  }

  /* ── Onboarding profile step ── */
  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.profileScroll} keyboardShouldPersistTaps="handled">
        <Text style={styles.logo}>🎓</Text>
        <Text style={styles.heading}>Set up your profile</Text>
        <Text style={styles.subText}>This takes under a minute.</Text>

        <View style={styles.card}>
          <Text style={styles.fieldLabel}>Your name *</Text>
          <TextInput
            style={styles.input}
            placeholder="Full name"
            placeholderTextColor={Colors.textMuted}
            value={name}
            onChangeText={setName}
            autoCapitalize="words"
            returnKeyType="next"
          />

          <Text style={styles.fieldLabel}>Department</Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. Computer Science"
            placeholderTextColor={Colors.textMuted}
            value={department}
            onChangeText={setDepartment}
            returnKeyType="next"
          />

          <Text style={styles.fieldLabel}>Year</Text>
          <TextInput
            style={styles.input}
            placeholder="1 – 4"
            placeholderTextColor={Colors.textMuted}
            value={year}
            onChangeText={(v) => setYear(v.replace(/\D/g, '').slice(0, 1))}
            keyboardType="number-pad"
            maxLength={1}
            returnKeyType="done"
          />

          <Text style={styles.sectionLabel}>Skills</Text>
          <Text style={styles.fieldLabel}>Skill name</Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. Figma"
            placeholderTextColor={Colors.textMuted}
            value={skillName}
            onChangeText={setSkillName}
            returnKeyType="next"
          />

          <Text style={styles.fieldLabel}>Skill level</Text>
          <View style={styles.choiceRow}>
            {SKILL_LEVELS.map((level) => (
              <TouchableOpacity
                key={level}
                style={[styles.choice, skillLevel === level && styles.choiceSelected]}
                onPress={() => setSkillLevel(level)}
                accessibilityRole="button"
                accessibilityState={{ selected: skillLevel === level }}
              >
                <Text style={[styles.choiceText, skillLevel === level && styles.choiceTextSelected]}>
                  {level}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.fieldLabel}>Sample links (up to 3, comma-separated)</Text>
          <TextInput
            style={styles.input}
            placeholder="https://…"
            placeholderTextColor={Colors.textMuted}
            value={sampleLinks}
            onChangeText={setSampleLinks}
            autoCapitalize="none"
            keyboardType="url"
          />

          <TouchableOpacity
            style={styles.secondaryBtn}
            onPress={handleAddSkill}
            activeOpacity={0.85}
          >
            <Text style={styles.secondaryBtnText}>Add skill</Text>
          </TouchableOpacity>

          {skills.map((skill, index) => (
            <View key={`${skill.skill_name}-${index}`} style={styles.skillEntry}>
              <View style={styles.skillInfo}>
                <Text style={styles.skillName}>{skill.skill_name}</Text>
                <Text style={styles.skillMeta}>
                  {skill.level} · {skill.sample_links?.length ?? 0} sample links
                </Text>
              </View>
              <TouchableOpacity
                onPress={() => setSkills((current) => current.filter((_, itemIndex) => itemIndex !== index))}
                accessibilityRole="button"
                accessibilityLabel={`Remove ${skill.skill_name}`}
              >
                <Text style={styles.removeText}>Remove</Text>
              </TouchableOpacity>
            </View>
          ))}

          <Text style={styles.sectionLabel}>Availability</Text>
          <Text style={styles.fieldLabel}>Current status</Text>
          <View style={styles.choiceRow}>
            {AVAILABILITY_STATUSES.map((status) => (
              <TouchableOpacity
                key={status}
                style={[styles.choice, availabilityStatus === status && styles.choiceSelected]}
                onPress={() => setAvailabilityStatus(status)}
                accessibilityRole="button"
                accessibilityState={{ selected: availabilityStatus === status }}
              >
                <Text style={[styles.choiceText, availabilityStatus === status && styles.choiceTextSelected]}>
                  {status}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.fieldLabel}>Available hours per week</Text>
          <TextInput
            style={styles.input}
            placeholder="10"
            placeholderTextColor={Colors.textMuted}
            value={hoursPerWeek}
            onChangeText={(value) => setHoursPerWeek(value.replace(/\D/g, '').slice(0, 3))}
            keyboardType="number-pad"
          />

          <TouchableOpacity
            style={[styles.btn, (isLoading || skills.length === 0) && styles.btnDisabled]}
            onPress={handleSaveProfile}
            disabled={isLoading || !name.trim() || skills.length === 0}
            activeOpacity={0.85}
          >
            <Text style={styles.btnText}>{isLoading ? 'Saving…' : 'Continue'}</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.bgDark,
    paddingHorizontal: Spacing.xl,
    justifyContent: 'center',
  },
  profileScroll: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingVertical: Spacing['3xl'],
  },
  back: {
    position: 'absolute',
    top: 60,
    left: Spacing.xl,
  },
  backText: {
    color: Colors.textOnDarkSecondary,
    fontSize: Typography.size.base,
    fontFamily: Typography.fontFamily.medium,
  },
  hero: {
    alignItems: 'center',
    marginBottom: Spacing.xl,
  },
  logo: {
    fontSize: 48,
    textAlign: 'center',
    marginBottom: Spacing.sm,
  },
  heading: {
    fontSize: Typography.size.xl,
    fontFamily: Typography.fontFamily.bold,
    color: Colors.textOnDark,
    textAlign: 'center',
    marginBottom: Spacing.xs,
  },
  subText: {
    fontSize: Typography.size.base,
    color: Colors.textOnDarkSecondary,
    textAlign: 'center',
    lineHeight: Typography.size.base * 1.6,
    fontFamily: Typography.fontFamily.regular,
  },
  emailText: {
    color: Colors.green,
    fontFamily: Typography.fontFamily.semiBold,
  },
  card: {
    backgroundColor: Colors.surfaceDark,
    borderRadius: Radii.lg,
    padding: Spacing.xl,
    borderWidth: 1,
    borderColor: Colors.borderDark,
  },
  otpInput: {
    backgroundColor: Colors.bgDark,
    borderWidth: 1,
    borderColor: Colors.borderDark,
    borderRadius: Radii.md,
    height: 64,
    fontSize: 32,
    fontFamily: Typography.fontFamily.bold,
    color: Colors.textOnDark,
    textAlign: 'center',
    letterSpacing: 12,
    marginBottom: Spacing.base,
  },
  fieldLabel: {
    fontSize: Typography.size.sm,
    color: Colors.textOnDarkSecondary,
    fontFamily: Typography.fontFamily.medium,
    marginBottom: Spacing.xs,
    marginTop: Spacing.sm,
  },
  sectionLabel: {
    fontSize: Typography.size.md,
    color: Colors.textOnDark,
    fontFamily: Typography.fontFamily.semiBold,
    marginTop: Spacing.lg,
    marginBottom: Spacing.xs,
  },
  input: {
    backgroundColor: Colors.bgDark,
    borderWidth: 1,
    borderColor: Colors.borderDark,
    borderRadius: Radii.md,
    paddingHorizontal: Spacing.base,
    height: 52,
    fontSize: Typography.size.base,
    color: Colors.textOnDark,
    fontFamily: Typography.fontFamily.regular,
    marginBottom: Spacing.xs,
  },
  choiceRow: {
    flexDirection: 'row',
    gap: Spacing.xs,
    marginBottom: Spacing.sm,
  },
  choice: {
    flex: 1,
    minHeight: 40,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: Spacing.xs,
    borderRadius: Radii.md,
    borderWidth: 1,
    borderColor: Colors.borderDark,
    backgroundColor: Colors.bgDark,
  },
  choiceSelected: {
    borderColor: Colors.green,
    backgroundColor: Colors.green,
  },
  choiceText: {
    color: Colors.textOnDarkSecondary,
    fontSize: Typography.size.xs,
    fontFamily: Typography.fontFamily.medium,
    textTransform: 'capitalize',
  },
  choiceTextSelected: {
    color: '#FFFFFF',
  },
  secondaryBtn: {
    minHeight: 44,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: Radii.md,
    borderWidth: 1,
    borderColor: Colors.green,
    marginTop: Spacing.xs,
  },
  secondaryBtnText: {
    color: Colors.green,
    fontFamily: Typography.fontFamily.semiBold,
    fontSize: Typography.size.sm,
  },
  skillEntry: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: Spacing.sm,
    paddingVertical: Spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: Colors.borderDark,
  },
  skillInfo: { flex: 1 },
  skillName: {
    color: Colors.textOnDark,
    fontFamily: Typography.fontFamily.medium,
    fontSize: Typography.size.sm,
  },
  skillMeta: {
    color: Colors.textOnDarkSecondary,
    fontFamily: Typography.fontFamily.regular,
    fontSize: Typography.size.xs,
    textTransform: 'capitalize',
  },
  removeText: {
    color: Colors.error,
    fontFamily: Typography.fontFamily.medium,
    fontSize: Typography.size.xs,
  },
  btn: {
    backgroundColor: Colors.green,
    borderRadius: Radii.button,
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: Spacing.base,
  },
  btnDisabled: { opacity: 0.5 },
  btnText: {
    color: '#FFFFFF',
    fontFamily: Typography.fontFamily.semiBold,
    fontSize: Typography.size.md,
  },
  hint: {
    textAlign: 'center',
    marginTop: Spacing.base,
    fontSize: Typography.size.sm,
    color: Colors.textOnDarkSecondary,
    fontFamily: Typography.fontFamily.regular,
  },
  link: {
    color: Colors.green,
    fontFamily: Typography.fontFamily.medium,
  },
});
