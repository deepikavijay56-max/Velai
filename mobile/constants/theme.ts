// Velai design tokens — source of truth for all UI styling
// §12 of PROJECT_CONTEXT_VELAI.md

export const Colors = {
  // Brand
  navy: '#0D1B3E',
  navyLight: '#1A2F5E',
  green: '#10B97A',
  greenLight: '#D1FAE5',
  amber: '#F59E0B',
  amberLight: '#FEF3C7',

  // Backgrounds
  bgLight: '#F5F7FF',
  bgDark: '#090E1A',
  cardLight: '#FFFFFF',
  cardDark: '#111827',
  surfaceDark: '#1C2537',

  // Text
  textPrimary: '#0D1B3E',
  textSecondary: '#6B7280',
  textMuted: '#9CA3AF',
  textOnDark: '#F9FAFB',
  textOnDarkSecondary: '#9CA3AF',

  // Borders
  border: '#E5E7EB',
  borderDark: '#1F2D47',

  // Status
  success: '#10B97A',
  warning: '#F59E0B',
  error: '#EF4444',
  errorLight: '#FEE2E2',
  info: '#3B82F6',

  // Gig status badge colours
  status: {
    Draft: { bg: '#F3F4F6', text: '#6B7280' },
    Open: { bg: '#D1FAE5', text: '#065F46' },
    InProgress: { bg: '#DBEAFE', text: '#1E40AF' },
    Delivered: { bg: '#FEF3C7', text: '#92400E' },
    Completed: { bg: '#D1FAE5', text: '#065F46' },
    Expired: { bg: '#F3F4F6', text: '#6B7280' },
    Cancelled: { bg: '#FEE2E2', text: '#991B1B' },
    Disputed: { bg: '#FEE2E2', text: '#991B1B' },
  } as Record<string, { bg: string; text: string }>,

  // Misc
  overlay: 'rgba(0,0,0,0.4)',
  overlayLight: 'rgba(9,14,26,0.06)',
};

export const Typography = {
  fontFamily: {
    regular: 'Inter_400Regular',
    medium: 'Inter_500Medium',
    semiBold: 'Inter_600SemiBold',
    bold: 'Inter_700Bold',
  },
  size: {
    xs: 11,
    sm: 13,
    base: 15,
    md: 16,
    lg: 18,
    xl: 22,
    '2xl': 26,
    '3xl': 32,
  },
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  base: 16,
  lg: 20,
  xl: 24,
  '2xl': 32,
  '3xl': 48,
};

export const Radii = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  full: 9999,
  button: 24,
  card: 12,
};

export const Shadow = {
  card: {
    shadowColor: '#0D1B3E',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.07,
    shadowRadius: 8,
    elevation: 3,
  },
  elevated: {
    shadowColor: '#0D1B3E',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.12,
    shadowRadius: 16,
    elevation: 8,
  },
};

export const Layout = {
  tabBarHeight: 64,
  headerHeight: 56,
  inputHeight: 48,
  buttonHeight: 52,
};
