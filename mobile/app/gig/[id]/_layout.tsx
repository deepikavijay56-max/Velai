/**
 * app/gig/[id]/_layout.tsx
 * Stack layout for the gig detail group.
 * Screens:  index (detail+apply), applicants, workspace
 */
import { Stack } from 'expo-router';
import { Colors, Typography } from '@/constants/theme';

export default function GigLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: Colors.bgLight },
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen name="index" />
      <Stack.Screen name="applicants" />
      <Stack.Screen name="workspace" />
    </Stack>
  );
}
