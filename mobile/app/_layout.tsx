/**
 * app/_layout.tsx
 * Root layout: loads fonts, wraps with AuthProvider, guards authenticated routes.
 * Uses a Stack so Expo Router knows the full screen hierarchy.
 */
import { AuthProvider, useAuth } from '@/hooks/useAuth';
import {
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
  Inter_700Bold,
  useFonts,
} from '@expo-google-fonts/inter';
import { Redirect, Stack, SplashScreen, useSegments } from 'expo-router';
import { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { View } from 'react-native';
import { Colors } from '@/constants/theme';

// Keep splash screen visible while fonts load
SplashScreen.preventAutoHideAsync();

function RootGuard() {
  const { isSignedIn, isLoading } = useAuth();
  const segments = useSegments();
  const isAuthRoute = segments[0] === '(auth)';
  const isLoginRoute = isAuthRoute && segments[1] === 'login';

  // Once auth resolves, hide the splash screen
  useEffect(() => {
    if (!isLoading) SplashScreen.hideAsync();
  }, [isLoading]);

  if (isLoading) {
    // Show blank dark screen while checking stored token
    return <View style={{ flex: 1, backgroundColor: Colors.bgDark }} />;
  }

  if (!isSignedIn && !isAuthRoute) {
    return <Redirect href="/(auth)/login" />;
  }

  if (isSignedIn && isLoginRoute) {
    return <Redirect href="/(tabs)" />;
  }

  // Authenticated: render the matched screen
  return (
    <Stack screenOptions={{ headerShown: false }}>
      {/* Tab navigator */}
      <Stack.Screen name="(tabs)" />
      {/* Auth group — accessible even when signed in (e.g. after sign-out) */}
      <Stack.Screen name="(auth)" />
      {/* Gig sub-stack */}
      <Stack.Screen name="gig/[id]" />
      {/* Misc */}
      <Stack.Screen name="+not-found" />
    </Stack>
  );
}

export default function RootLayout() {
  const [fontsLoaded] = useFonts({
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
    Inter_700Bold,
  });

  if (!fontsLoaded) return null;

  return (
    <AuthProvider>
      <StatusBar style="auto" />
      <RootGuard />
    </AuthProvider>
  );
}
