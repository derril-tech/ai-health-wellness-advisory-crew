import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { z } from 'zod';
import type { 
  User, 
  HealthProfile, 
  Program, 
  MacroTargets, 
  Workout, 
  WorkoutLog, 
  Habit, 
  Checkin, 
  Adjustment 
} from './types';

export class HealthCrewClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:3001/api/v1', token?: string) {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    // Add request interceptor for auth
    this.client.interceptors.request.use((config) => {
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Auth methods
  async login(email: string, password: string): Promise<{ token: string; user: User }> {
    const response = await this.client.post('/auth/login', { email, password });
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<{ token: string }> {
    const response = await this.client.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  }

  // User methods
  async getMe(): Promise<User> {
    const response = await this.client.get('/me');
    return response.data;
  }

  async updateMe(data: Partial<User>): Promise<User> {
    const response = await this.client.patch('/me', data);
    return response.data;
  }

  // Intake & Safety methods
  async submitIntake(questionnaire: any): Promise<HealthProfile> {
    const response = await this.client.post('/intake', questionnaire);
    return response.data;
  }

  async submitClearance(acknowledged: boolean): Promise<{ cleared: boolean }> {
    const response = await this.client.post('/intake/clearance', { acknowledged });
    return response.data;
  }

  // Program methods
  async createProgram(data: { start_date: string; goal: any }): Promise<Program> {
    const response = await this.client.post('/programs', data);
    return response.data;
  }

  async getProgram(programId: string): Promise<Program> {
    const response = await this.client.get(`/programs/${programId}`);
    return response.data;
  }

  async activateProgram(programId: string): Promise<Program> {
    const response = await this.client.post(`/programs/${programId}/activate`);
    return response.data;
  }

  // Nutrition methods
  async getMacros(programId: string, week: number): Promise<MacroTargets> {
    const response = await this.client.get(`/programs/${programId}/macros?week=${week}`);
    return response.data;
  }

  async getMealPlans(programId: string, week: number, day?: number): Promise<any> {
    const params = new URLSearchParams({ week: week.toString() });
    if (day !== undefined) params.append('day', day.toString());
    const response = await this.client.get(`/programs/${programId}/meal-plans?${params}`);
    return response.data;
  }

  // Training methods
  async getWorkouts(programId: string, week: number): Promise<Workout[]> {
    const response = await this.client.get(`/programs/${programId}/workouts?week=${week}`);
    return response.data;
  }

  async logWorkout(workoutId: string, sets: any[]): Promise<WorkoutLog[]> {
    const response = await this.client.post(`/workouts/${workoutId}/log`, { sets });
    return response.data;
  }

  // Habits methods
  async getHabits(programId: string): Promise<Habit[]> {
    const response = await this.client.get(`/programs/${programId}/habits`);
    return response.data;
  }

  async logHabit(habitId: string, value: number, note?: string): Promise<any> {
    const response = await this.client.post(`/habits/${habitId}/log`, { value, note });
    return response.data;
  }

  // Check-in methods
  async submitCheckin(programId: string, data: {
    metrics: any;
    photos?: any[];
  }): Promise<Checkin> {
    const response = await this.client.post(`/programs/${programId}/checkin`, data);
    return response.data;
  }

  async getAdjustments(programId: string): Promise<Adjustment[]> {
    const response = await this.client.get(`/programs/${programId}/adjustments`);
    return response.data;
  }

  // Device methods
  async connectDevice(provider: string): Promise<{ auth_url: string }> {
    const response = await this.client.post(`/devices/connect/${provider}`);
    return response.data;
  }

  async syncDevices(window: string): Promise<{ synced: boolean }> {
    const response = await this.client.post('/devices/sync', { window });
    return response.data;
  }

  // Export methods
  async exportProgram(programId: string, targets: string[]): Promise<{ export_id: string }> {
    const response = await this.client.post(`/programs/${programId}/export`, { targets });
    return response.data;
  }

  async getExport(exportId: string): Promise<{ status: string; download_url?: string }> {
    const response = await this.client.get(`/exports/${exportId}`);
    return response.data;
  }
}
