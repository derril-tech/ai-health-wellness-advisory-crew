import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const checkinSuccessRate = new Rate('checkin_success_rate');
const checkinDuration = new Trend('checkin_duration');
const deviceSyncSuccessRate = new Rate('device_sync_success_rate');
const deviceSyncDuration = new Trend('device_sync_duration');
const concurrentUsers = new Counter('concurrent_users');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10 },  // Ramp up to 10 users
    { duration: '5m', target: 10 },  // Stay at 10 users
    { duration: '2m', target: 50 },  // Ramp up to 50 users
    { duration: '5m', target: 50 },  // Stay at 50 users
    { duration: '2m', target: 100 }, // Ramp up to 100 users
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 0 },   // Ramp down to 0 users
  ],
  thresholds: {
    'checkin_duration': ['p(95)<2000'], // 95% of check-ins should complete within 2s
    'device_sync_duration': ['p(95)<5000'], // 95% of device syncs should complete within 5s
    'checkin_success_rate': ['rate>0.95'], // 95% success rate for check-ins
    'device_sync_success_rate': ['rate>0.90'], // 90% success rate for device syncs
    'http_req_duration': ['p(95)<3000'], // 95% of HTTP requests should complete within 3s
    'http_req_failed': ['rate<0.05'], // Less than 5% of requests should fail
  },
};

// Test data
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const USERS = JSON.parse(__ENV.USERS || '[]');

// Helper function to get random user
function getRandomUser() {
  if (USERS.length === 0) {
    // Generate mock user data if none provided
    return {
      id: `user_${Math.floor(Math.random() * 1000)}`,
      email: `user${Math.floor(Math.random() * 1000)}@example.com`,
      token: `token_${Math.floor(Math.random() * 1000000)}`,
    };
  }
  return USERS[Math.floor(Math.random() * USERS.length)];
}

// Helper function to generate check-in data
function generateCheckinData() {
  const weight = 70 + Math.random() * 10; // 70-80 kg
  const bodyFat = 15 + Math.random() * 10; // 15-25%
  const sleepQuality = Math.floor(Math.random() * 10) + 1; // 1-10
  const stressLevel = Math.floor(Math.random() * 10) + 1; // 1-10
  const energyLevel = Math.floor(Math.random() * 10) + 1; // 1-10
  const mood = Math.floor(Math.random() * 10) + 1; // 1-10

  return {
    weight: weight.toFixed(1),
    body_fat: bodyFat.toFixed(1),
    sleep_quality: sleepQuality,
    stress_level: stressLevel,
    energy_level: energyLevel,
    mood: mood,
    notes: `Load test check-in - ${new Date().toISOString()}`,
  };
}

// Helper function to generate device data
function generateDeviceData() {
  const steps = Math.floor(Math.random() * 15000) + 5000; // 5k-20k steps
  const heartRate = 60 + Math.floor(Math.random() * 40); // 60-100 bpm
  const hrv = 20 + Math.floor(Math.random() * 30); // 20-50 ms
  const sleepHours = 6 + Math.random() * 3; // 6-9 hours

  return {
    steps: steps,
    heart_rate: heartRate,
    hrv: hrv,
    sleep_hours: sleepHours.toFixed(1),
    sleep_quality: Math.floor(Math.random() * 10) + 1, // 1-10
    timestamp: new Date().toISOString(),
  };
}

// Main test function
export default function() {
  const user = getRandomUser();
  concurrentUsers.add(1);

  // Set headers for authentication
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${user.token}`,
  };

  // Test 1: Weekly Check-in
  const checkinData = generateCheckinData();
  const checkinStart = Date.now();
  
  const checkinResponse = http.post(
    `${BASE_URL}/api/v1/check-ins`,
    JSON.stringify({
      user_id: user.id,
      program_id: `program_${user.id}`,
      week_number: Math.floor(Math.random() * 12) + 1,
      weight: checkinData.weight,
      body_fat: checkinData.body_fat,
      sleep_quality: checkinData.sleep_quality,
      stress_level: checkinData.stress_level,
      energy_level: checkinData.energy_level,
      mood: checkinData.mood,
      notes: checkinData.notes,
    }),
    { headers }
  );

  const checkinDuration_ms = Date.now() - checkinStart;
  checkinDuration.add(checkinDuration_ms);

  const checkinSuccess = check(checkinResponse, {
    'check-in status is 201': (r) => r.status === 201,
    'check-in response has id': (r) => r.json('id') !== undefined,
    'check-in response has analysis': (r) => r.json('progress_analysis') !== undefined,
  });

  checkinSuccessRate.add(checkinSuccess);

  // Test 2: Device Sync (Fitbit)
  const deviceData = generateDeviceData();
  const deviceSyncStart = Date.now();

  const deviceSyncResponse = http.post(
    `${BASE_URL}/api/v1/devices/sync/fitbit`,
    JSON.stringify({
      user_id: user.id,
      device_id: `fitbit_${user.id}`,
      data: {
        steps: deviceData.steps,
        heart_rate: deviceData.heart_rate,
        hrv: deviceData.hrv,
        sleep: {
          hours: deviceData.sleep_hours,
          quality: deviceData.sleep_quality,
        },
        timestamp: deviceData.timestamp,
      },
    }),
    { headers }
  );

  const deviceSyncDuration_ms = Date.now() - deviceSyncStart;
  deviceSyncDuration.add(deviceSyncDuration_ms);

  const deviceSyncSuccess = check(deviceSyncResponse, {
    'device sync status is 200': (r) => r.status === 200,
    'device sync response has sync_id': (r) => r.json('sync_id') !== undefined,
    'device sync response has processed': (r) => r.json('processed') === true,
  });

  deviceSyncSuccessRate.add(deviceSyncSuccess);

  // Test 3: Get Progress Analysis
  const progressResponse = http.get(
    `${BASE_URL}/api/v1/check-ins/${user.id}/progress`,
    { headers }
  );

  check(progressResponse, {
    'progress analysis status is 200': (r) => r.status === 200,
    'progress analysis has weight_trend': (r) => r.json('weight_trend') !== undefined,
    'progress analysis has adherence': (r) => r.json('adherence') !== undefined,
  });

  // Test 4: Get Adjustments
  const adjustmentsResponse = http.get(
    `${BASE_URL}/api/v1/programs/${user.id}/adjustments`,
    { headers }
  );

  check(adjustmentsResponse, {
    'adjustments status is 200': (r) => r.status === 200,
    'adjustments is array': (r) => Array.isArray(r.json()),
  });

  // Test 5: Apply Adjustments
  if (adjustmentsResponse.status === 200 && adjustmentsResponse.json().length > 0) {
    const adjustment = adjustmentsResponse.json()[0];
    
    const applyResponse = http.post(
      `${BASE_URL}/api/v1/programs/${user.id}/adjustments/${adjustment.id}/apply`,
      JSON.stringify({
        user_id: user.id,
        applied_at: new Date().toISOString(),
      }),
      { headers }
    );

    check(applyResponse, {
      'apply adjustment status is 200': (r) => r.status === 200,
      'adjustment applied successfully': (r) => r.json('applied') === true,
    });
  }

  // Test 6: Concurrent Nutrition Logging
  const nutritionData = {
    meal_type: 'breakfast',
    calories: Math.floor(Math.random() * 500) + 200,
    protein: Math.floor(Math.random() * 30) + 10,
    carbs: Math.floor(Math.random() * 50) + 20,
    fats: Math.floor(Math.random() * 20) + 5,
  };

  const nutritionResponse = http.post(
    `${BASE_URL}/api/v1/nutrition/log`,
    JSON.stringify({
      user_id: user.id,
      program_id: `program_${user.id}`,
      ...nutritionData,
    }),
    { headers }
  );

  check(nutritionResponse, {
    'nutrition logging status is 201': (r) => r.status === 201,
    'nutrition log has id': (r) => r.json('id') !== undefined,
  });

  // Test 7: Concurrent Workout Logging
  const workoutData = {
    workout_id: `workout_${Math.floor(Math.random() * 100)}`,
    exercises: [
      {
        exercise_id: 'bench_press',
        sets: [
          { weight: 80, reps: 8, completed: true },
          { weight: 80, reps: 8, completed: true },
        ],
      },
    ],
    duration_minutes: Math.floor(Math.random() * 60) + 30,
    completed: true,
  };

  const workoutResponse = http.post(
    `${BASE_URL}/api/v1/training/log`,
    JSON.stringify({
      user_id: user.id,
      program_id: `program_${user.id}`,
      ...workoutData,
    }),
    { headers }
  );

  check(workoutResponse, {
    'workout logging status is 201': (r) => r.status === 201,
    'workout log has id': (r) => r.json('id') !== undefined,
  });

  // Test 8: Concurrent Habit Tracking
  const habitData = {
    habit_id: `habit_${Math.floor(Math.random() * 5) + 1}`,
    completed: Math.random() > 0.3, // 70% completion rate
    notes: 'Load test habit completion',
  };

  const habitResponse = http.post(
    `${BASE_URL}/api/v1/habits/track`,
    JSON.stringify({
      user_id: user.id,
      program_id: `program_${user.id}`,
      ...habitData,
    }),
    { headers }
  );

  check(habitResponse, {
    'habit tracking status is 201': (r) => r.status === 201,
    'habit log has id': (r) => r.json('id') !== undefined,
  });

  // Test 9: Schedule Optimization (less frequent)
  if (Math.random() < 0.1) { // 10% chance
    const scheduleResponse = http.post(
      `${BASE_URL}/api/v1/schedule/optimize`,
      JSON.stringify({
        user_id: user.id,
        program_id: `program_${user.id}`,
        preferences: {
          workout_days: ['monday', 'wednesday', 'friday'],
          meal_prep_time: 30,
          quiet_hours: { start: '22:00', end: '07:00' },
        },
      }),
      { headers }
    );

    check(scheduleResponse, {
      'schedule optimization status is 200': (r) => r.status === 200,
      'schedule has optimized_workouts': (r) => r.json('optimized_workouts') !== undefined,
    });
  }

  // Test 10: Report Generation (less frequent)
  if (Math.random() < 0.05) { // 5% chance
    const reportResponse = http.post(
      `${BASE_URL}/api/v1/reports/generate`,
      JSON.stringify({
        user_id: user.id,
        program_id: `program_${user.id}`,
        report_type: 'weekly_summary',
        week_number: Math.floor(Math.random() * 12) + 1,
        format: 'pdf',
      }),
      { headers }
    );

    check(reportResponse, {
      'report generation status is 200': (r) => r.status === 200,
      'report has download_url': (r) => r.json('download_url') !== undefined,
    });
  }

  // Random sleep between requests to simulate real user behavior
  sleep(Math.random() * 2 + 1); // 1-3 seconds
}

// Setup function to prepare test data
export function setup() {
  console.log('Setting up load test data...');
  
  // Create test users if not provided
  if (USERS.length === 0) {
    console.log('No test users provided, using mock data');
  } else {
    console.log(`Using ${USERS.length} test users`);
  }

  return {
    baseUrl: BASE_URL,
    userCount: USERS.length || 1000, // Default to 1000 mock users
  };
}

// Teardown function to clean up
export function teardown(data) {
  console.log('Cleaning up load test data...');
  console.log(`Test completed with ${data.userCount} users`);
}
