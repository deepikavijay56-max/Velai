/**
 * components/ChatBubble.tsx
 * Single message bubble in the workspace chat.
 */
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Colors, Radii, Spacing, Typography } from '../constants/theme';
import { Message } from '../lib/api';

interface Props {
  message: Message;
  isMine: boolean;
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function ChatBubble({ message, isMine }: Props) {
  return (
    <View style={[styles.wrapper, isMine ? styles.wrapperMine : styles.wrapperTheirs]}>
      <View style={[styles.bubble, isMine ? styles.bubbleMine : styles.bubbleTheirs]}>
        {message.attachment_url && (
          <Text style={styles.attachment}>📎 Attachment</Text>
        )}
        <Text style={[styles.body, isMine ? styles.bodyMine : styles.bodyTheirs]}>
          {message.body}
        </Text>
        <Text style={[styles.time, isMine ? styles.timeMine : styles.timeTheirs]}>
          {formatTime(message.created_at)}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    paddingHorizontal: Spacing.base,
    marginBottom: Spacing.sm,
  },
  wrapperMine: {
    alignItems: 'flex-end',
  },
  wrapperTheirs: {
    alignItems: 'flex-start',
  },
  bubble: {
    maxWidth: '78%',
    borderRadius: Radii.lg,
    padding: Spacing.md,
  },
  bubbleMine: {
    backgroundColor: Colors.navy,
    borderBottomRightRadius: 4,
  },
  bubbleTheirs: {
    backgroundColor: Colors.cardLight,
    borderWidth: 1,
    borderColor: Colors.border,
    borderBottomLeftRadius: 4,
  },
  attachment: {
    fontSize: Typography.size.sm,
    color: Colors.amber,
    marginBottom: Spacing.xs,
    fontFamily: Typography.fontFamily.medium,
  },
  body: {
    fontSize: Typography.size.base,
    lineHeight: Typography.size.base * 1.5,
  },
  bodyMine: {
    color: '#FFFFFF',
    fontFamily: Typography.fontFamily.regular,
  },
  bodyTheirs: {
    color: Colors.textPrimary,
    fontFamily: Typography.fontFamily.regular,
  },
  time: {
    fontSize: Typography.size.xs,
    marginTop: Spacing.xs,
    textAlign: 'right',
  },
  timeMine: {
    color: 'rgba(255,255,255,0.6)',
  },
  timeTheirs: {
    color: Colors.textMuted,
  },
});
