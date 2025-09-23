/**
 * User State Validator
 * Provides utilities to validate user state consistency between frontend and backend
 */

export interface UserStateValidation {
  isValid: boolean;
  issues: string[];
  recommendations: string[];
}

export interface UserStateData {
  clerkUser: any;
  backendUser: any;
  preferences: any;
  competitors: any[];
  onboardingComplete: boolean;
}

/**
 * Validates user state consistency
 */
export function validateUserState(data: UserStateData): UserStateValidation {
  const issues: string[] = [];
  const recommendations: string[] = [];

  // Check if user exists in both systems
  if (!data.clerkUser && !data.backendUser) {
    issues.push('User not found in both Clerk and backend');
    recommendations.push('User needs to complete authentication');
    return { isValid: false, issues, recommendations };
  }

  if (!data.clerkUser) {
    issues.push('User not found in Clerk');
    recommendations.push('User needs to sign in again');
  }

  if (!data.backendUser) {
    issues.push('User not found in backend');
    recommendations.push('User needs to be synced with backend');
  }

  // Check onboarding completion consistency
  const frontendOnboardingComplete = data.clerkUser?.unsafeMetadata?.onboardingComplete === true;
  const backendOnboardingComplete = data.onboardingComplete;

  if (frontendOnboardingComplete !== backendOnboardingComplete) {
    issues.push('Onboarding completion status mismatch between frontend and backend');
    if (frontendOnboardingComplete && !backendOnboardingComplete) {
      recommendations.push('Backend data may be incomplete. Consider refreshing user status.');
    } else if (!frontendOnboardingComplete && backendOnboardingComplete) {
      recommendations.push('Frontend state may be outdated. Consider refreshing user status.');
    }
  }

  // Check if backend has required data for completion
  if (backendOnboardingComplete) {
    const hasValidPreferences = data.preferences && 
      data.preferences.industry && 
      data.preferences.marketing_goals && 
      data.preferences.marketing_goals.length > 0 &&
      data.preferences.company_size;

    const hasCompetitors = data.competitors && data.competitors.length > 0;

    if (!hasValidPreferences) {
      issues.push('Backend marked as complete but preferences are invalid');
      recommendations.push('User preferences need to be updated');
    }

    if (!hasCompetitors) {
      issues.push('Backend marked as complete but no competitors found');
      recommendations.push('User needs to add at least one competitor');
    }
  }

  // Check for data integrity
  if (data.preferences) {
    const industry = data.preferences.industry?.trim();
    const goals = data.preferences.marketing_goals || [];
    const validGoals = goals.filter((goal: string) => goal && goal.trim());

    if (!industry) {
      issues.push('Industry is empty or invalid');
      recommendations.push('User needs to select a valid industry');
    }

    if (validGoals.length === 0) {
      issues.push('No valid marketing goals selected');
      recommendations.push('User needs to select at least one marketing goal');
    }
  }

  return {
    isValid: issues.length === 0,
    issues,
    recommendations
  };
}

/**
 * Determines the correct redirect path based on validation
 */
export function getCorrectRedirectPath(validation: UserStateValidation, currentPath: string): string | null {
  if (validation.isValid) {
    // If valid, check if we're on the right page
    if (currentPath.startsWith('/dashboard') || currentPath.startsWith('/welcome')) {
      return null; // Already on correct page
    }
    return 'dashboard';
  } else {
    // If invalid, check if we're on onboarding
    if (currentPath.startsWith('/onboarding')) {
      return null; // Already on correct page
    }
    return 'onboarding';
  }
}

/**
 * Creates a user-friendly error message from validation issues
 */
export function createUserFriendlyMessage(validation: UserStateValidation): string {
  if (validation.isValid) {
    return 'User state is valid';
  }

  if (validation.issues.length === 1) {
    return validation.issues[0];
  }

  return `Multiple issues found: ${validation.issues.join(', ')}`;
}

/**
 * Checks if user should be redirected based on current state
 */
export function shouldRedirectUser(
  currentPath: string,
  frontendComplete: boolean,
  backendComplete: boolean,
  hasValidData: boolean
): { shouldRedirect: boolean; targetPath: string | null; reason: string } {
  // If both frontend and backend agree on completion
  if (frontendComplete === backendComplete) {
    if (backendComplete && hasValidData) {
      // User is complete and should be on dashboard
      if (!currentPath.startsWith('/dashboard') && !currentPath.startsWith('/welcome')) {
        return {
          shouldRedirect: true,
          targetPath: 'dashboard',
          reason: 'User onboarding is complete'
        };
      }
    } else {
      // User is not complete and should be on onboarding
      if (!currentPath.startsWith('/onboarding')) {
        return {
          shouldRedirect: true,
          targetPath: 'onboarding',
          reason: 'User onboarding is incomplete'
        };
      }
    }
  } else {
    // Frontend and backend disagree - this is a problem
    if (frontendComplete && !backendComplete) {
      return {
        shouldRedirect: true,
        targetPath: 'onboarding',
        reason: 'Backend data is incomplete despite frontend completion'
      };
    } else if (!frontendComplete && backendComplete) {
      return {
        shouldRedirect: true,
        targetPath: 'dashboard',
        reason: 'Frontend state is outdated despite backend completion'
      };
    }
  }

  return {
    shouldRedirect: false,
    targetPath: null,
    reason: 'No redirect needed'
  };
}
