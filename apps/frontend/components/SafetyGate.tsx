'use client';

import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, XCircle, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';

interface SafetyWarning {
  type: 'error' | 'warning' | 'info';
  message: string;
  requiresAction?: boolean;
}

interface SafetyGateProps {
  profile: {
    risk_level: 'low' | 'medium' | 'high';
    parq_flags: string[];
    cleared: boolean;
    bmi?: number;
    injuries: Array<{
      type: string;
      location: string;
      severity: string;
      recovery_status: string;
    }>;
    medications: Array<{
      name: string;
      purpose: string;
    }>;
  };
  onAcknowledge: (acknowledged: boolean) => void;
  onContinue: () => void;
}

export function SafetyGate({ profile, onAcknowledge, onContinue }: SafetyGateProps) {
  const [acknowledged, setAcknowledged] = useState(false);

  const generateWarnings = (): SafetyWarning[] => {
    const warnings: SafetyWarning[] = [];

    // High risk profile
    if (profile.risk_level === 'high') {
      warnings.push({
        type: 'error',
        message: 'High risk profile detected. Medical clearance required before starting any exercise program.',
        requiresAction: true,
      });
    }

    // PAR-Q flags
    if (profile.parq_flags.length > 0) {
      warnings.push({
        type: 'error',
        message: 'PAR-Q screening indicates potential health risks. Please consult with a healthcare provider.',
        requiresAction: true,
      });
    }

    // High BMI
    if (profile.bmi && profile.bmi >= 35) {
      warnings.push({
        type: 'warning',
        message: 'High BMI detected. Consider consulting with a healthcare provider before starting exercise.',
      });
    }

    // Active injuries
    const activeInjuries = profile.injuries.filter(i => i.recovery_status !== 'recovered');
    if (activeInjuries.length > 0) {
      warnings.push({
        type: 'warning',
        message: 'Active injuries detected. Medical clearance recommended before exercise.',
      });
    }

    // Medications
    if (profile.medications.length > 0) {
      warnings.push({
        type: 'info',
        message: 'Medications detected. Consult with healthcare provider about exercise interactions.',
      });
    }

    return warnings;
  };

  const warnings = generateWarnings();
  const hasBlockingWarnings = warnings.some(w => w.type === 'error' && w.requiresAction);
  const canProceed = profile.cleared && !hasBlockingWarnings;

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getWarningIcon = (type: string) => {
    switch (type) {
      case 'error': return <XCircle className="h-4 w-4" />;
      case 'warning': return <AlertTriangle className="h-4 w-4" />;
      case 'info': return <Info className="h-4 w-4" />;
      default: return <Info className="h-4 w-4" />;
    }
  };

  const getWarningVariant = (type: string) => {
    switch (type) {
      case 'error': return 'destructive';
      case 'warning': return 'default';
      case 'info': return 'default';
      default: return 'default';
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {canProceed ? (
              <CheckCircle className="h-6 w-6 text-green-600" />
            ) : (
              <AlertTriangle className="h-6 w-6 text-red-600" />
            )}
            Safety Assessment
          </CardTitle>
          <CardDescription>
            Review your health profile and safety status before proceeding
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Risk Level */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="font-medium">Risk Level:</span>
            <Badge className={getRiskLevelColor(profile.risk_level)}>
              {profile.risk_level.toUpperCase()}
            </Badge>
          </div>

          {/* Clearance Status */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="font-medium">Clearance Status:</span>
            <div className="flex items-center gap-2">
              {profile.cleared ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <XCircle className="h-5 w-5 text-red-600" />
              )}
              <span className={profile.cleared ? 'text-green-600' : 'text-red-600'}>
                {profile.cleared ? 'Cleared' : 'Not Cleared'}
              </span>
            </div>
          </div>

          {/* Warnings */}
          {warnings.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-medium text-gray-900">Safety Warnings</h3>
              {warnings.map((warning, index) => (
                <Alert key={index} variant={getWarningVariant(warning.type) as any}>
                  {getWarningIcon(warning.type)}
                  <AlertDescription>{warning.message}</AlertDescription>
                </Alert>
              ))}
            </div>
          )}

          {/* PAR-Q Flags */}
          {profile.parq_flags.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-medium text-gray-900">PAR-Q Screening Results</h3>
              <div className="space-y-2">
                {profile.parq_flags.map((flag, index) => (
                  <div key={index} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <span className="text-sm text-red-800">{flag}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col gap-3 pt-4">
            {hasBlockingWarnings ? (
              <div className="space-y-3">
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    Medical clearance is required before you can proceed with your program.
                  </AlertDescription>
                </Alert>
                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => onAcknowledge(false)}
                    className="flex-1"
                  >
                    I Understand - Get Medical Clearance
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="acknowledge"
                    checked={acknowledged}
                    onChange={(e) => setAcknowledged(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <label htmlFor="acknowledge" className="text-sm text-gray-700">
                    I acknowledge the safety warnings and understand the risks involved
                  </label>
                </div>
                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => onAcknowledge(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => {
                      onAcknowledge(true);
                      onContinue();
                    }}
                    disabled={!acknowledged}
                    className="flex-1"
                  >
                    Continue to Program
                  </Button>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
