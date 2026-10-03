/**
 * app/(tabs)/_layout.tsx
 * Bottom tab navigator with the 5 required tabs from the spec.
 * The Post tab is large and central (§12).
 */
import { Tabs } from 'expo-router';
import { Platform, StyleSheet, Text, View } from 'react-native';
import { Colors, Typography } from '@/constants/theme';

function TabIcon({ label, emoji, focused }: { label: string; emoji: string; focused: boolean }) {
  return (
    <View style={styles.tabItem}>
      <Text style={[styles.tabEmoji, focused && styles.tabEmojiFocused]}>{emoji}</Text>
      <Text style={[styles.tabLabel, focused && styles.tabLabelFocused]}>{label}</Text>
    </View>
  );
}

function PostIcon({ focused }: { focused: boolean }) {
  return (
    <View style={[styles.postBtn, focused && styles.postBtnFocused]}>
      <Text style={styles.postIcon}>+</Text>
    </View>
  );
}

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: styles.tabBar,
        tabBarShowLabel: false,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Gigs',
          tabBarIcon: ({ focused }) => (
            <TabIcon label="Gigs" emoji="🔍" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="my-work"
        options={{
          title: 'My work',
          tabBarIcon: ({ focused }) => (
            <TabIcon label="My work" emoji="💼" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="post"
        options={{
          title: 'Post',
          tabBarIcon: ({ focused }) => <PostIcon focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="chats"
        options={{
          title: 'Chats',
          tabBarIcon: ({ focused }) => (
            <TabIcon label="Chats" emoji="💬" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="me"
        options={{
          title: 'Me',
          tabBarIcon: ({ focused }) => (
            <TabIcon label="Me" emoji="👤" focused={focused} />
          ),
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: Colors.cardLight,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    height: Platform.OS === 'ios' ? 84 : 64,
    paddingBottom: Platform.OS === 'ios' ? 24 : 8,
    paddingTop: 8,
  },
  tabItem: {
    alignItems: 'center',
    gap: 3,
  },
  tabEmoji: {
    fontSize: 22,
    opacity: 0.4,
  },
  tabEmojiFocused: {
    opacity: 1,
  },
  tabLabel: {
    fontSize: Typography.size.xs,
    color: Colors.textMuted,
    fontFamily: Typography.fontFamily.medium,
  },
  tabLabelFocused: {
    color: Colors.navy,
  },
  postBtn: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: Colors.border,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  postBtnFocused: {
    backgroundColor: Colors.navy,
  },
  postIcon: {
    fontSize: 28,
    color: '#FFFFFF',
    lineHeight: 32,
    fontFamily: Typography.fontFamily.bold,
  },
});
