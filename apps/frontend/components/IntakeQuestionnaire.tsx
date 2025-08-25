'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';

const intakeSchema = z.object({
  // Basic Information
  height_cm: z.number().min(100).max(250),
  weight_kg: z.number().min(30).max(300),
  age: z.number().min(13).max(100),
  sex_at_birth: z.enum(['male', 'female', 'other']),
  
  // Activity & Goals
  activity_level: z.enum(['sedentary', 'light', 'moderate', 'active', 'very_active']),
  goal: z.enum(['lose_weight', 'gain_muscle', 'maintain', 'improve_fitness', 'sports_performance']),
  experience_level: z.enum(['beginner', 'intermediate', 'advanced']),
  
  // Equipment & Preferences
  equipment_access: z.array(z.string()),
  allergies: z.array(z.string()),
  
  // Health Information
  injuries: z.array(z.object({
    type: z.string(),
    location: z.string(),
    severity: z.enum(['mild', 'moderate', 'severe']),
    recovery_status: z.enum(['recovered', 'recovering', 'active']),
    notes: z.string().optional(),
  })),
  
  medications: z.array(z.object({
    name: z.string(),
    dosage: z.string(),
    frequency: z.string(),
    purpose: z.string(),
    notes: z.string().optional(),
  })),
  
  // PAR-Q Screening
  parq_responses: z.object({
    parq_1: z.boolean(),
    parq_2: z.boolean(),
    parq_3: z.boolean(),
    parq_4: z.boolean(),
    parq_5: z.boolean(),
    parq_6: z.boolean(),
    parq_7: z.boolean(),
  }),
});

type IntakeFormData = z.infer<typeof intakeSchema>;

interface IntakeQuestionnaireProps {
  onSubmit: (data: IntakeFormData) => void;
  onCancel: () => void;
}

const parqQuestions = [
  "Has your doctor ever said that you have a heart condition?",
  "Do you feel pain in your chest when you do physical activity?",
  "In the past month, have you had chest pain when you were not doing physical activity?",
  "Do you lose your balance because of dizziness or do you ever lose consciousness?",
  "Do you have a bone or joint problem that could be made worse by a change in your physical activity?",
  "Is your doctor currently prescribing drugs for your blood pressure or heart condition?",
  "Do you know of any other reason why you should not do physical activity?"
];

export function IntakeQuestionnaire({ onSubmit, onCancel }: IntakeQuestionnaireProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 5;
  
  const form = useForm<IntakeFormData>({
    resolver: zodResolver(intakeSchema),
    defaultValues: {
      equipment_access: [],
      allergies: [],
      injuries: [],
      medications: [],
      parq_responses: {
        parq_1: false,
        parq_2: false,
        parq_3: false,
        parq_4: false,
        parq_5: false,
        parq_6: false,
        parq_7: false,
      },
    },
  });

  const handleSubmit = (data: IntakeFormData) => {
    onSubmit(data);
  };

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderBasicInfo = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="height_cm">Height (cm)</Label>
          <Input
            id="height_cm"
            type="number"
            {...form.register('height_cm', { valueAsNumber: true })}
          />
        </div>
        <div>
          <Label htmlFor="weight_kg">Weight (kg)</Label>
          <Input
            id="weight_kg"
            type="number"
            {...form.register('weight_kg', { valueAsNumber: true })}
          />
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="age">Age</Label>
          <Input
            id="age"
            type="number"
            {...form.register('age', { valueAsNumber: true })}
          />
        </div>
        <div>
          <Label htmlFor="sex_at_birth">Sex at Birth</Label>
          <Select onValueChange={(value) => form.setValue('sex_at_birth', value as any)}>
            <SelectTrigger>
              <SelectValue placeholder="Select sex" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="male">Male</SelectItem>
              <SelectItem value="female">Female</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );

  const renderActivityGoals = () => (
    <div className="space-y-4">
      <div>
        <Label htmlFor="activity_level">Current Activity Level</Label>
        <Select onValueChange={(value) => form.setValue('activity_level', value as any)}>
          <SelectTrigger>
            <SelectValue placeholder="Select activity level" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="sedentary">Sedentary (little to no exercise)</SelectItem>
            <SelectItem value="light">Light (1-3 days/week)</SelectItem>
            <SelectItem value="moderate">Moderate (3-5 days/week)</SelectItem>
            <SelectItem value="active">Active (6-7 days/week)</SelectItem>
            <SelectItem value="very_active">Very Active (2x training/day)</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div>
        <Label htmlFor="goal">Primary Goal</Label>
        <Select onValueChange={(value) => form.setValue('goal', value as any)}>
          <SelectTrigger>
            <SelectValue placeholder="Select your goal" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="lose_weight">Lose Weight</SelectItem>
            <SelectItem value="gain_muscle">Gain Muscle</SelectItem>
            <SelectItem value="maintain">Maintain Current</SelectItem>
            <SelectItem value="improve_fitness">Improve Fitness</SelectItem>
            <SelectItem value="sports_performance">Sports Performance</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div>
        <Label htmlFor="experience_level">Fitness Experience</Label>
        <Select onValueChange={(value) => form.setValue('experience_level', value as any)}>
          <SelectTrigger>
            <SelectValue placeholder="Select experience level" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="beginner">Beginner (0-1 years)</SelectItem>
            <SelectItem value="intermediate">Intermediate (1-3 years)</SelectItem>
            <SelectItem value="advanced">Advanced (3+ years)</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );

  const renderEquipmentAllergies = () => (
    <div className="space-y-4">
      <div>
        <Label>Equipment Access</Label>
        <div className="grid grid-cols-2 gap-2 mt-2">
          {['dumbbells', 'barbell', 'resistance_bands', 'pull_up_bar', 'bench', 'cardio_machine', 'none'].map((equipment) => (
            <div key={equipment} className="flex items-center space-x-2">
              <Checkbox
                id={equipment}
                checked={form.watch('equipment_access').includes(equipment)}
                onCheckedChange={(checked) => {
                  const current = form.watch('equipment_access');
                  if (checked) {
                    form.setValue('equipment_access', [...current, equipment]);
                  } else {
                    form.setValue('equipment_access', current.filter(e => e !== equipment));
                  }
                }}
              />
              <Label htmlFor={equipment} className="text-sm capitalize">
                {equipment.replace('_', ' ')}
              </Label>
            </div>
          ))}
        </div>
      </div>
      
      <div>
        <Label htmlFor="allergies">Food Allergies (comma-separated)</Label>
        <Textarea
          id="allergies"
          placeholder="e.g., nuts, dairy, shellfish"
          value={form.watch('allergies').join(', ')}
          onChange={(e) => {
            const allergies = e.target.value.split(',').map(a => a.trim()).filter(a => a);
            form.setValue('allergies', allergies);
          }}
        />
      </div>
    </div>
  );

  const renderHealthInfo = () => (
    <div className="space-y-4">
      <div>
        <Label>Injuries & Medical Conditions</Label>
        <div className="space-y-2 mt-2">
          {form.watch('injuries').map((_, index) => (
            <Card key={index} className="p-3">
              <div className="grid grid-cols-2 gap-2">
                <Input
                  placeholder="Type of injury"
                  value={form.watch(`injuries.${index}.type`)}
                  onChange={(e) => form.setValue(`injuries.${index}.type`, e.target.value)}
                />
                <Input
                  placeholder="Location"
                  value={form.watch(`injuries.${index}.location`)}
                  onChange={(e) => form.setValue(`injuries.${index}.location`, e.target.value)}
                />
                <Select
                  value={form.watch(`injuries.${index}.severity`)}
                  onValueChange={(value) => form.setValue(`injuries.${index}.severity`, value as any)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Severity" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="mild">Mild</SelectItem>
                    <SelectItem value="moderate">Moderate</SelectItem>
                    <SelectItem value="severe">Severe</SelectItem>
                  </SelectContent>
                </Select>
                <Select
                  value={form.watch(`injuries.${index}.recovery_status`)}
                  onValueChange={(value) => form.setValue(`injuries.${index}.recovery_status`, value as any)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="recovered">Recovered</SelectItem>
                    <SelectItem value="recovering">Recovering</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </Card>
          ))}
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              const current = form.watch('injuries');
              form.setValue('injuries', [...current, { type: '', location: '', severity: 'mild', recovery_status: 'recovered' }]);
            }}
          >
            Add Injury
          </Button>
        </div>
      </div>
    </div>
  );

  const renderPARQ = () => (
    <div className="space-y-4">
      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="font-medium text-blue-900 mb-2">Physical Activity Readiness Questionnaire (PAR-Q)</h3>
        <p className="text-sm text-blue-700">
          Please answer the following questions to help us assess your readiness for physical activity.
        </p>
      </div>
      
      <div className="space-y-4">
        {parqQuestions.map((question, index) => (
          <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg">
            <Checkbox
              id={`parq_${index + 1}`}
              checked={form.watch(`parq_responses.parq_${index + 1}`)}
              onCheckedChange={(checked) => {
                form.setValue(`parq_responses.parq_${index + 1}`, checked as boolean);
              }}
            />
            <Label htmlFor={`parq_${index + 1}`} className="text-sm leading-relaxed">
              {question}
            </Label>
          </div>
        ))}
      </div>
    </div>
  );

  const renderStep = () => {
    switch (currentStep) {
      case 1: return renderBasicInfo();
      case 2: return renderActivityGoals();
      case 3: return renderEquipmentAllergies();
      case 4: return renderHealthInfo();
      case 5: return renderPARQ();
      default: return null;
    }
  };

  const getStepTitle = () => {
    switch (currentStep) {
      case 1: return 'Basic Information';
      case 2: return 'Activity & Goals';
      case 3: return 'Equipment & Allergies';
      case 4: return 'Health Information';
      case 5: return 'Safety Screening';
      default: return '';
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Health & Fitness Assessment</CardTitle>
          <CardDescription>
            Let's get to know you better to create your personalized program
          </CardDescription>
          
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>Step {currentStep} of {totalSteps}</span>
              <span>{Math.round((currentStep / totalSteps) * 100)}% Complete</span>
            </div>
            <Progress value={(currentStep / totalSteps) * 100} />
          </div>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <div>
              <h3 className="text-lg font-medium mb-4">{getStepTitle()}</h3>
              {renderStep()}
            </div>
            
            <div className="flex justify-between pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={prevStep}
                disabled={currentStep === 1}
              >
                Previous
              </Button>
              
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={onCancel}
                >
                  Cancel
                </Button>
                
                {currentStep < totalSteps ? (
                  <Button
                    type="button"
                    onClick={nextStep}
                  >
                    Next
                  </Button>
                ) : (
                  <Button type="submit">
                    Submit Assessment
                  </Button>
                )}
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
