import { test, expect } from '@playwright/test';

test.describe('User Journey E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:3000');
  });

  test('Complete onboarding flow', async ({ page }) => {
    // Test the complete onboarding journey
    await test.step('Landing page and sign up', async () => {
      await expect(page.locator('h1')).toContainText('Health & Wellness Advisor');
      await page.click('text=Get Started');
      
      // Should navigate to sign up
      await expect(page).toHaveURL(/.*signup/);
    });

    await test.step('User registration', async () => {
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'TestPassword123!');
      await page.fill('[data-testid="confirm-password-input"]', 'TestPassword123!');
      await page.click('[data-testid="signup-button"]');
      
      // Should navigate to onboarding
      await expect(page).toHaveURL(/.*onboarding/);
    });

    await test.step('Health screening (PAR-Q)', async () => {
      // Answer PAR-Q questions
      await page.click('[data-testid="parq-chest-pain-no"]');
      await page.click('[data-testid="parq-balance-no"]');
      await page.click('[data-testid="parq-bone-problems-no"]');
      await page.click('[data-testid="parq-blood-pressure-no"]');
      await page.click('[data-testid="parq-other-reasons-no"]');
      await page.click('[data-testid="parq-age-yes"]');
      
      await page.click('[data-testid="continue-button"]');
      
      // Should show safety clearance
      await expect(page.locator('[data-testid="safety-clearance"]')).toBeVisible();
    });

    await test.step('Profile setup', async () => {
      await page.fill('[data-testid="first-name-input"]', 'John');
      await page.fill('[data-testid="last-name-input"]', 'Doe');
      await page.fill('[data-testid="age-input"]', '30');
      await page.fill('[data-testid="weight-input"]', '75');
      await page.fill('[data-testid="height-input"]', '175');
      await page.selectOption('[data-testid="gender-select"]', 'male');
      await page.selectOption('[data-testid="activity-select"]', 'moderately_active');
      await page.selectOption('[data-testid="goal-select"]', 'weight_loss');
      
      await page.click('[data-testid="continue-button"]');
    });

    await test.step('Program generation', async () => {
      // Should show program generation progress
      await expect(page.locator('[data-testid="program-generating"]')).toBeVisible();
      
      // Wait for program to be generated
      await expect(page.locator('[data-testid="program-complete"]')).toBeVisible({ timeout: 30000 });
      
      // Should show program summary
      await expect(page.locator('[data-testid="program-summary"]')).toBeVisible();
      await expect(page.locator('text=12-Week Weight Loss')).toBeVisible();
    });

    await test.step('Navigate to dashboard', async () => {
      await page.click('[data-testid="start-program-button"]');
      
      // Should be on dashboard
      await expect(page).toHaveURL(/.*dashboard/);
      await expect(page.locator('[data-testid="today-view"]')).toBeVisible();
    });
  });

  test('Daily program execution', async ({ page }) => {
    // Login and navigate to dashboard
    await page.goto('http://localhost:3000/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-button"]');
    
    await expect(page).toHaveURL(/.*dashboard/);

    await test.step('View today\'s program', async () => {
      await expect(page.locator('[data-testid="today-view"]')).toBeVisible();
      await expect(page.locator('[data-testid="workout-card"]')).toBeVisible();
      await expect(page.locator('[data-testid="nutrition-card"]')).toBeVisible();
      await expect(page.locator('[data-testid="habits-card"]')).toBeVisible();
    });

    await test.step('Complete workout', async () => {
      await page.click('[data-testid="start-workout-button"]');
      
      // Should open workout player
      await expect(page.locator('[data-testid="workout-player"]')).toBeVisible();
      
      // Complete first exercise
      await page.click('[data-testid="exercise-1"]');
      await page.fill('[data-testid="weight-input"]', '80');
      await page.fill('[data-testid="reps-input"]', '8');
      await page.click('[data-testid="complete-set-button"]');
      
      // Mark workout as complete
      await page.click('[data-testid="complete-workout-button"]');
      
      // Should show completion
      await expect(page.locator('[data-testid="workout-complete"]')).toBeVisible();
    });

    await test.step('Log nutrition', async () => {
      await page.click('[data-testid="nutrition-tab"]');
      
      // Log breakfast
      await page.click('[data-testid="log-breakfast-button"]');
      await page.fill('[data-testid="calories-input"]', '500');
      await page.fill('[data-testid="protein-input"]', '30');
      await page.fill('[data-testid="carbs-input"]', '50');
      await page.fill('[data-testid="fats-input"]', '20');
      await page.click('[data-testid="save-meal-button"]');
      
      // Should show logged meal
      await expect(page.locator('[data-testid="logged-meal"]')).toBeVisible();
    });

    await test.step('Complete habits', async () => {
      await page.click('[data-testid="habits-tab"]');
      
      // Complete a habit
      await page.click('[data-testid="habit-1-checkbox"]');
      
      // Should show habit as completed
      await expect(page.locator('[data-testid="habit-1-completed"]')).toBeVisible();
    });
  });

  test('Weekly check-in flow', async ({ page }) => {
    // Login and navigate to check-ins
    await page.goto('http://localhost:3000/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-button"]');
    
    await page.click('[data-testid="check-ins-nav"]');

    await test.step('Start weekly check-in', async () => {
      await expect(page.locator('[data-testid="check-ins-page"]')).toBeVisible();
      await page.click('[data-testid="start-checkin-button"]');
      
      // Should open check-in wizard
      await expect(page.locator('[data-testid="checkin-wizard"]')).toBeVisible();
    });

    await test.step('Complete check-in steps', async () => {
      // Step 1: Weight and measurements
      await page.fill('[data-testid="weight-input"]', '74.5');
      await page.fill('[data-testid="body-fat-input"]', '18.5');
      await page.click('[data-testid="next-step-button"]');
      
      // Step 2: Sleep and recovery
      await page.selectOption('[data-testid="sleep-quality-select"]', '7');
      await page.selectOption('[data-testid="stress-level-select"]', '5');
      await page.selectOption('[data-testid="energy-level-select"]', '8');
      await page.click('[data-testid="next-step-button"]');
      
      // Step 3: Mood and notes
      await page.selectOption('[data-testid="mood-select"]', '7');
      await page.fill('[data-testid="notes-input"]', 'Feeling good this week, workouts are getting easier');
      await page.click('[data-testid="next-step-button"]');
      
      // Step 4: Review and submit
      await expect(page.locator('[data-testid="checkin-summary"]')).toBeVisible();
      await page.click('[data-testid="submit-checkin-button"]');
    });

    await test.step('View progress analysis', async () => {
      // Should show progress analysis
      await expect(page.locator('[data-testid="progress-analysis"]')).toBeVisible();
      await expect(page.locator('[data-testid="weight-trend"]')).toBeVisible();
      await expect(page.locator('[data-testid="adherence-metrics"]')).toBeVisible();
    });

    await test.step('Review adjustments', async () => {
      await page.click('[data-testid="view-adjustments-button"]');
      
      // Should show recommended adjustments
      await expect(page.locator('[data-testid="adjustments-preview"]')).toBeVisible();
      await expect(page.locator('[data-testid="calorie-adjustment"]')).toBeVisible();
      
      // Apply adjustments
      await page.click('[data-testid="apply-adjustments-button"]');
      
      // Should confirm adjustments applied
      await expect(page.locator('[data-testid="adjustments-applied"]')).toBeVisible();
    });
  });

  test('Nutrition and meal planning', async ({ page }) => {
    // Login and navigate to nutrition
    await page.goto('http://localhost:3000/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-button"]');
    
    await page.click('[data-testid="nutrition-nav"]');

    await test.step('View meal plan', async () => {
      await expect(page.locator('[data-testid="nutrition-page"]')).toBeVisible();
      await expect(page.locator('[data-testid="meal-plan"]')).toBeVisible();
      await expect(page.locator('[data-testid="macro-targets"]')).toBeVisible();
    });

    await test.step('Food swap functionality', async () => {
      await page.click('[data-testid="swap-food-button"]');
      
      // Should open swap modal
      await expect(page.locator('[data-testid="swap-modal"]')).toBeVisible();
      
      // Search for alternative
      await page.fill('[data-testid="food-search-input"]', 'chicken breast');
      await page.click('[data-testid="search-button"]');
      
      // Select alternative
      await page.click('[data-testid="food-option-1"]');
      await page.click('[data-testid="confirm-swap-button"]');
      
      // Should update meal plan
      await expect(page.locator('[data-testid="updated-meal"]')).toBeVisible();
    });

    await test.step('Generate grocery list', async () => {
      await page.click('[data-testid="grocery-list-button"]');
      
      // Should show grocery list
      await expect(page.locator('[data-testid="grocery-list"]')).toBeVisible();
      await expect(page.locator('[data-testid="grocery-item"]')).toBeVisible();
      
      // Export grocery list
      await page.click('[data-testid="export-grocery-button"]');
      
      // Should trigger download
      const downloadPromise = page.waitForEvent('download');
      await page.click('[data-testid="download-csv-button"]');
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toContain('grocery-list');
    });
  });

  test('Training and workout management', async ({ page }) => {
    // Login and navigate to training
    await page.goto('http://localhost:3000/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-button"]');
    
    await page.click('[data-testid="training-nav"]');

    await test.step('View workout schedule', async () => {
      await expect(page.locator('[data-testid="training-page"]')).toBeVisible();
      await expect(page.locator('[data-testid="workout-schedule"]')).toBeVisible();
      await expect(page.locator('[data-testid="workout-card"]')).toBeVisible();
    });

    await test.step('Exercise substitution', async () => {
      await page.click('[data-testid="substitute-exercise-button"]');
      
      // Should open substitution modal
      await expect(page.locator('[data-testid="substitution-modal"]')).toBeVisible();
      
      // Search for alternative exercise
      await page.fill('[data-testid="exercise-search-input"]', 'push-up');
      await page.click('[data-testid="search-button"]');
      
      // Select alternative
      await page.click('[data-testid="exercise-option-1"]');
      await page.click('[data-testid="confirm-substitution-button"]');
      
      // Should update workout
      await expect(page.locator('[data-testid="updated-workout"]')).toBeVisible();
    });

    await test.step('Workout logging', async () => {
      await page.click('[data-testid="log-workout-button"]');
      
      // Should open workout logger
      await expect(page.locator('[data-testid="workout-logger"]')).toBeVisible();
      
      // Log sets for first exercise
      await page.fill('[data-testid="set-1-weight"]', '80');
      await page.fill('[data-testid="set-1-reps"]', '8');
      await page.click('[data-testid="log-set-button"]');
      
      await page.fill('[data-testid="set-2-weight"]', '80');
      await page.fill('[data-testid="set-2-reps"]', '8');
      await page.click('[data-testid="log-set-button"]');
      
      // Complete workout
      await page.click('[data-testid="complete-workout-button"]');
      
      // Should show completion
      await expect(page.locator('[data-testid="workout-complete"]')).toBeVisible();
    });
  });

  test('Reports and analytics', async ({ page }) => {
    // Login and navigate to reports
    await page.goto('http://localhost:3000/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-button"]');
    
    await page.click('[data-testid="reports-nav"]');

    await test.step('View progress charts', async () => {
      await expect(page.locator('[data-testid="reports-page"]')).toBeVisible();
      await expect(page.locator('[data-testid="progress-charts"]')).toBeVisible();
      await expect(page.locator('[data-testid="weight-chart"]')).toBeVisible();
      await expect(page.locator('[data-testid="macro-chart"]')).toBeVisible();
    });

    await test.step('Export reports', async () => {
      await page.click('[data-testid="export-report-button"]');
      
      // Should open export dialog
      await expect(page.locator('[data-testid="export-dialog"]')).toBeVisible();
      
      // Select export options
      await page.click('[data-testid="weekly-summary-pdf"]');
      await page.click('[data-testid="export-button"]');
      
      // Should trigger download
      const downloadPromise = page.waitForEvent('download');
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toContain('weekly-summary');
    });

    await test.step('View PR logbook', async () => {
      await page.click('[data-testid="pr-logbook-tab"]');
      
      // Should show PR records
      await expect(page.locator('[data-testid="pr-logbook"]')).toBeVisible();
      await expect(page.locator('[data-testid="pr-record"]')).toBeVisible();
    });
  });

  test('Error handling and edge cases', async ({ page }) => {
    await test.step('Invalid login credentials', async () => {
      await page.goto('http://localhost:3000/login');
      await page.fill('[data-testid="email-input"]', 'invalid@example.com');
      await page.fill('[data-testid="password-input"]', 'wrongpassword');
      await page.click('[data-testid="login-button"]');
      
      // Should show error message
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
      await expect(page.locator('text=Invalid credentials')).toBeVisible();
    });

    await test.step('Network error handling', async () => {
      // Simulate network error by going offline
      await page.context().setOffline(true);
      
      await page.goto('http://localhost:3000/dashboard');
      
      // Should show offline message
      await expect(page.locator('[data-testid="offline-message"]')).toBeVisible();
      
      // Go back online
      await page.context().setOffline(false);
      
      // Should recover
      await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();
    });

    await test.step('Form validation', async () => {
      await page.goto('http://localhost:3000/signup');
      
      // Try to submit without required fields
      await page.click('[data-testid="signup-button"]');
      
      // Should show validation errors
      await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
    });
  });
});
