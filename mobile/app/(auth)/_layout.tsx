/**
 * app/(auth)/_layout.tsx
 * Layout for unauthenticated screens (no tab bar).
 */
import { Stack } from 'expo-router';
import { Colors } from '@/constants/theme';

export default function AuthLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: Colors.bgDark },
        animation: 'slide_from_right',
      }}
    />
  );
}
