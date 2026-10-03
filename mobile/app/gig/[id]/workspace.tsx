/**
 * app/gig/[id]/workspace.tsx
 * Gig workspace: real-time chat, deliverables, and agreement confirmation.
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Alert,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { useChat } from '@/hooks/useChat';
import { useAuth } from '@/hooks/useAuth';
import { contractsApi, Contract, deliverablesApi, Message } from '@/lib/api';
import { ChatBubble } from '@/components/ChatBubble';
import { RatingModal } from '@/components/RatingModal';
import { reviewsApi } from '@/lib/api';
import { Colors, Radii, Spacing, Typography } from '@/constants/theme';

export default function WorkspaceScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { user } = useAuth();
  const { messages, isLoading, isSending, sendMessage, currentUserId } = useChat(id);

  const [contract, setContract] = useState<Contract | null>(null);
  const [contractError, setContractError] = useState<string | null>(null);
  const [deliveryUrl, setDeliveryUrl] = useState('');
  const [deliveryNote, setDeliveryNote] = useState('');
  const [isUpdatingContract, setIsUpdatingContract] = useState(false);
  const [text, setText] = useState('');
  const [showRating, setShowRating] = useState(false);
  const [isSubmittingRating, setIsSubmittingRating] = useState(false);
  const listRef = useRef<FlatList>(null);

  const loadContract = useCallback(async () => {
    try {
      const { data } = await contractsApi.getByGig(id);
      setContract(data);
      setContractError(null);
    } catch {
      setContractError('Could not load the contract. Return to My Work and try again.');
    }
  }, [id]);

  useEffect(() => {
    void loadContract();
  }, [loadContract]);

  async function handleSend() {
    if (!text.trim()) return;
    const body = text.trim();
    setText('');
    await sendMessage(body);
    listRef.current?.scrollToEnd({ animated: true });
  }

  function renderMessage({ item }: { item: Message }) {
    return <ChatBubble message={item} isMine={item.sender_id === currentUserId} />;
  }

  const isDoer = contract?.doer_id === user?.id;
  const pendingDeliverable = contract?.deliverables
    .filter((deliverable) => deliverable.status === 'submitted')
    .sort((first, second) => second.version - first.version)[0];

  async function handleConfirmContract() {
    if (!contract) return;
    setIsUpdatingContract(true);
    try {
      const { data } = await contractsApi.confirm(contract.id);
      setContract(data);
    } catch {
      Alert.alert('Error', 'Could not confirm the agreement. Try again.');
    } finally {
      setIsUpdatingContract(false);
    }
  }

  async function handleDeliver() {
    if (!contract || !deliveryUrl.trim()) {
      Alert.alert('Deliverable link required', 'Add a link to your completed work.');
      return;
    }
    setIsUpdatingContract(true);
    try {
      await contractsApi.deliver(contract.id, {
        file_url: deliveryUrl.trim(),
        note: deliveryNote.trim(),
      });
      setDeliveryUrl('');
      setDeliveryNote('');
      await loadContract();
    } catch {
      Alert.alert('Error', 'Could not submit the deliverable. Try again.');
    } finally {
      setIsUpdatingContract(false);
    }
  }

  async function handleApprove(deliverable: Contract['deliverables'][number]) {
    setIsUpdatingContract(true);
    try {
      await deliverablesApi.approve(deliverable.id);
      await loadContract();
    } catch {
      Alert.alert('Error', 'Could not approve the deliverable. Try again.');
    } finally {
      setIsUpdatingContract(false);
    }
  }

  async function handleRatingSubmit(rating: number, reviewText: string, tags: string[]) {
    if (!contract) return;
    setIsSubmittingRating(true);
    try {
      await reviewsApi.create(contract.id, { rating, comment: reviewText, tags });
      setShowRating(false);
      Alert.alert('Rating submitted', 'Thanks for your feedback!');
    } catch {
      Alert.alert('Error', 'Could not submit rating. Try again.');
    } finally {
      setIsSubmittingRating(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 88 : 0}
    >
      <SafeAreaView style={styles.safe}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()}>
            <Text style={styles.backText}>←</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle} numberOfLines={1}>
            Workspace
          </Text>
          {contract?.status === 'completed' && (
            <TouchableOpacity onPress={() => setShowRating(true)}>
              <Text style={styles.rateBtn}>Rate ★</Text>
            </TouchableOpacity>
          )}
        </View>

        {contractError ? (
          <Text style={styles.workflowError}>{contractError}</Text>
        ) : contract?.status === 'pending_confirmation' ? (
          <View style={styles.workflow}>
            <Text style={styles.workflowText}>Confirm the agreement to start this gig.</Text>
            {contract.doer_id === user?.id && !contract.confirmed_by_doer_at && (
              <TouchableOpacity
                style={styles.workflowButton}
                onPress={handleConfirmContract}
                disabled={isUpdatingContract}
              >
                <Text style={styles.workflowButtonText}>
                  {isUpdatingContract ? 'Confirming…' : 'Confirm agreement'}
                </Text>
              </TouchableOpacity>
            )}
          </View>
        ) : contract?.status === 'active' && isDoer ? (
          <View style={styles.workflow}>
            <Text style={styles.workflowText}>Submit your completed work.</Text>
            <TextInput
              style={styles.workflowInput}
              placeholder="Deliverable URL"
              placeholderTextColor={Colors.textMuted}
              value={deliveryUrl}
              onChangeText={setDeliveryUrl}
              autoCapitalize="none"
            />
            <TextInput
              style={[styles.workflowInput, styles.workflowNote]}
              placeholder="Note (optional)"
              placeholderTextColor={Colors.textMuted}
              value={deliveryNote}
              onChangeText={setDeliveryNote}
              multiline
            />
            <TouchableOpacity
              style={styles.workflowButton}
              onPress={handleDeliver}
              disabled={isUpdatingContract}
            >
              <Text style={styles.workflowButtonText}>
                {isUpdatingContract ? 'Submitting…' : 'Submit deliverable'}
              </Text>
            </TouchableOpacity>
          </View>
        ) : pendingDeliverable && !isDoer ? (
          <View style={styles.workflow}>
            <Text style={styles.workflowText}>
              Submitted work: {pendingDeliverable.file_url}
            </Text>
            <TouchableOpacity
              style={styles.workflowButton}
              onPress={() => handleApprove(pendingDeliverable)}
              disabled={isUpdatingContract}
            >
              <Text style={styles.workflowButtonText}>
                {isUpdatingContract ? 'Approving…' : 'Approve deliverable'}
              </Text>
            </TouchableOpacity>
          </View>
        ) : null}

        {/* Messages */}
        {isLoading ? (
          <View style={styles.loadingWrap}>
            <Text style={styles.loadingText}>Loading messages…</Text>
          </View>
        ) : (
          <FlatList
            ref={listRef}
            data={messages}
            keyExtractor={(m) => m.id}
            renderItem={renderMessage}
            contentContainerStyle={styles.messageList}
            onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: false })}
            showsVerticalScrollIndicator={false}
            ListEmptyComponent={
              <View style={styles.emptyChat}>
                <Text style={styles.emptyChatIcon}>💬</Text>
                <Text style={styles.emptyChatText}>
                  No messages yet. Say hello to get started!
                </Text>
              </View>
            }
          />
        )}

        {/* Input bar */}
        <View style={styles.inputBar}>
          <TextInput
            style={styles.input}
            placeholder="Type a message…"
            placeholderTextColor={Colors.textMuted}
            value={text}
            onChangeText={setText}
            multiline
            maxLength={2000}
            returnKeyType="send"
            onSubmitEditing={handleSend}
            blurOnSubmit={false}
          />
          <TouchableOpacity
            style={[styles.sendBtn, (!text.trim() || isSending) && styles.sendBtnDisabled]}
            onPress={handleSend}
            disabled={!text.trim() || isSending}
            activeOpacity={0.85}
          >
            <Text style={styles.sendIcon}>{isSending ? '…' : '↑'}</Text>
          </TouchableOpacity>
        </View>

        {/* Rating modal */}
        <RatingModal
          visible={showRating}
          onSubmit={handleRatingSubmit}
          onDismiss={() => setShowRating(false)}
          isSubmitting={isSubmittingRating}
        />
      </SafeAreaView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.bgLight },
  safe: { flex: 1 },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.base,
    paddingVertical: Spacing.md,
    backgroundColor: Colors.cardLight,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
    gap: Spacing.sm,
  },
  workflow: {
    padding: Spacing.base,
    backgroundColor: Colors.cardLight,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
    gap: Spacing.sm,
  },
  workflowText: {
    color: Colors.textPrimary,
    fontSize: Typography.size.sm,
    fontFamily: Typography.fontFamily.medium,
  },
  workflowError: {
    paddingHorizontal: Spacing.base,
    paddingVertical: Spacing.sm,
    color: Colors.error,
  },
  workflowInput: {
    backgroundColor: Colors.bgLight,
    borderRadius: Radii.md,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingHorizontal: Spacing.base,
    height: 44,
    color: Colors.textPrimary,
  },
  workflowNote: { height: 72, textAlignVertical: 'top', paddingVertical: Spacing.sm },
  workflowButton: {
    alignSelf: 'flex-start',
    backgroundColor: Colors.green,
    borderRadius: Radii.button,
    paddingHorizontal: Spacing.base,
    paddingVertical: Spacing.sm,
  },
  workflowButtonText: {
    color: '#FFFFFF',
    fontFamily: Typography.fontFamily.semiBold,
  },
  backText: { fontSize: 22, color: Colors.navy, fontFamily: Typography.fontFamily.bold },
  headerTitle: {
    flex: 1,
    fontSize: Typography.size.lg,
    fontFamily: Typography.fontFamily.semiBold,
    color: Colors.textPrimary,
  },
  rateBtn: {
    fontSize: Typography.size.sm,
    color: Colors.amber,
    fontFamily: Typography.fontFamily.semiBold,
  },
  loadingWrap: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  loadingText: { color: Colors.textSecondary, fontSize: Typography.size.base },
  messageList: { paddingVertical: Spacing.md, flexGrow: 1 },
  emptyChat: { flex: 1, alignItems: 'center', paddingTop: Spacing['3xl'] },
  emptyChatIcon: { fontSize: 48, marginBottom: Spacing.base },
  emptyChatText: {
    fontSize: Typography.size.base,
    color: Colors.textSecondary,
    textAlign: 'center',
    fontFamily: Typography.fontFamily.regular,
    paddingHorizontal: Spacing.xl,
  },
  inputBar: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: Spacing.base,
    paddingVertical: Spacing.sm,
    backgroundColor: Colors.cardLight,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    gap: Spacing.sm,
  },
  input: {
    flex: 1,
    backgroundColor: Colors.bgLight,
    borderRadius: Radii.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingHorizontal: Spacing.base,
    paddingVertical: Spacing.sm,
    fontSize: Typography.size.base,
    color: Colors.textPrimary,
    fontFamily: Typography.fontFamily.regular,
    maxHeight: 120,
  },
  sendBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: Colors.navy,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendBtnDisabled: { opacity: 0.4 },
  sendIcon: { color: '#FFFFFF', fontSize: 20, fontFamily: Typography.fontFamily.bold },
});
