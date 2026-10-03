/**
 * app/(auth)/login.tsx
 * College-email OTP request screen.
 */
import React, { useState } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { authApi, parseError } from '@/lib/api';
import { Colors, Radii, Spacing, Typography } from '@/constants/theme';

const COLLEGE_DOMAIN = 'psgtech.ac.in'; // change to your college domain

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  async function handleRequestOtp() {
    if (!email.toLowerCase().endsWith(`@${COLLEGE_DOMAIN}`)) {
      Alert.alert(
        'College email required',
        `Use your @${COLLEGE_DOMAIN} email to sign in.`
      );
      return;
    }
    setIsLoading(true);
    try {
      await authApi.requestOtp(email.toLowerCase().trim());
      router.push({ pathname: '/(auth)/verify', params: { email } });
    } catch (error) {
      Alert.alert('Error', parseError(error).message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      {/* Hero */}
      <View style={styles.hero}>
        <Text style={styles.logo}>⚡ Velai</Text>
        <Text style={styles.tagline}>The campus gig marketplace</Text>
        <Text style={styles.subTagline}>Turn your skills into income. Build a verified portfolio.</Text>
      </View>

      {/* Card */}
      <View style={styles.card}>
        <Text style={styles.heading}>Sign in</Text>
        <Text style={styles.hint}>Use your @{COLLEGE_DOMAIN} email</Text>

        <TextInput
          style={styles.input}
          placeholder={`you@${COLLEGE_DOMAIN}`}
          placeholderTextColor={Colors.textMuted}
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
          autoCorrect={false}
          returnKeyType="send"
          onSubmitEditing={handleRequestOtp}
          accessibilityLabel="College email address"
        />

        <TouchableOpacity
          style={[styles.btn, isLoading && styles.btnDisabled]}
          onPress={handleRequestOtp}
          disabled={isLoading || !email}
          activeOpacity={0.85}
          accessibilityRole="button"
        >
          <Text style={styles.btnText}>{isLoading ? 'Sending OTP…' : 'Send OTP'}</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.footer}>
        Only students and staff of {COLLEGE_DOMAIN.split('.')[0].toUpperCase()} can sign in.
      </Text>
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
  hero: {
    alignItems: 'center',
    marginBottom: Spacing['2xl'],
  },
  logo: {
    fontSize: 48,
    marginBottom: Spacing.sm,
  },
  tagline: {
    fontSize: Typography.size.xl,
    fontFamily: Typography.fontFamily.bold,
    color: Colors.textOnDark,
    textAlign: 'center',
  },
  subTagline: {
    fontSize: Typography.size.base,
    color: Colors.textOnDarkSecondary,
    textAlign: 'center',
    marginTop: Spacing.sm,
    lineHeight: Typography.size.base * 1.6,
    fontFamily: Typography.fontFamily.regular,
  },
  card: {
    backgroundColor: Colors.surfaceDark,
    borderRadius: Radii.lg,
    padding: Spacing.xl,
    borderWidth: 1,
    borderColor: Colors.borderDark,
  },
  heading: {
    fontSize: Typography.size.lg,
    fontFamily: Typography.fontFamily.bold,
    color: Colors.textOnDark,
    marginBottom: Spacing.xs,
  },
  hint: {
    fontSize: Typography.size.sm,
    color: Colors.textOnDarkSecondary,
    marginBottom: Spacing.base,
    fontFamily: Typography.fontFamily.regular,
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
    marginBottom: Spacing.base,
  },
  btn: {
    backgroundColor: Colors.green,
    borderRadius: Radii.button,
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnDisabled: {
    opacity: 0.5,
  },
  btnText: {
    color: '#FFFFFF',
    fontFamily: Typography.fontFamily.semiBold,
    fontSize: Typography.size.md,
  },
  footer: {
    textAlign: 'center',
    marginTop: Spacing.lg,
    fontSize: Typography.size.sm,
    color: Colors.textOnDarkSecondary,
    fontFamily: Typography.fontFamily.regular,
  },
});
