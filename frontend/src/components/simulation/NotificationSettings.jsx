import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { useNotifications } from '@/hooks/useNotifications';
import {
    BellIcon,
    BellSlashIcon,
    Cog6ToothIcon,
    ExclamationTriangleIcon,
    InformationCircleIcon
} from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';

const NotificationSettings = ({ className = "" }) => {
    const { showSuccess, showError, showWarning, showInfo, clearAllNotifications } = useNotifications();

    // Notification preferences stored in localStorage
    const [settings, setSettings] = useState(() => {
        const saved = localStorage.getItem('notificationSettings');
        return saved ? JSON.parse(saved) : {
            enabled: true,
            showConnectionErrors: true,
            showSimulationEvents: true,
            showDeviceErrors: true,
            showRetryAttempts: true,
            errorDuration: 8000,
            warningDuration: 5000,
            successDuration: 3000,
            maxNotifications: 5,
            soundEnabled: false
        };
    });

    // Save settings to localStorage whenever they change
    useEffect(() => {
        localStorage.setItem('notificationSettings', JSON.stringify(settings));
    }, [settings]);

    const updateSetting = (key, value) => {
        setSettings(prev => ({ ...prev, [key]: value }));
    };

    const testNotifications = () => {
        showSuccess('This is a test success notification', { title: 'Test Success' });
        setTimeout(() => {
            showWarning('This is a test warning notification', { title: 'Test Warning' });
        }, 1000);
        setTimeout(() => {
            showError('This is a test error notification', { title: 'Test Error' });
        }, 2000);
        setTimeout(() => {
            showInfo('This is a test info notification', { title: 'Test Info' });
        }, 3000);
    };

    const resetToDefaults = () => {
        const defaults = {
            enabled: true,
            showConnectionErrors: true,
            showSimulationEvents: true,
            showDeviceErrors: true,
            showRetryAttempts: true,
            errorDuration: 8000,
            warningDuration: 5000,
            successDuration: 3000,
            maxNotifications: 5,
            soundEnabled: false
        };
        setSettings(defaults);
        showSuccess('Notification settings reset to defaults');
    };

    return (
        <Card className={className}>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center space-x-2">
                        <Cog6ToothIcon className="w-5 h-5" />
                        <span>Notification Settings</span>
                    </CardTitle>
                    <div className="flex items-center space-x-2">
                        <Button
                            size="sm"
                            variant="outline"
                            onClick={testNotifications}
                            className="text-xs"
                        >
                            Test Notifications
                        </Button>
                        <Button
                            size="sm"
                            variant="outline"
                            onClick={clearAllNotifications}
                            className="text-xs"
                        >
                            Clear All
                        </Button>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="space-y-6">
                {/* Master Enable/Disable */}
                <div className="flex items-center justify-between p-3 rounded-lg border">
                    <div className="flex items-center space-x-3">
                        {settings.enabled ? (
                            <BellIcon className="w-5 h-5 text-blue-600" />
                        ) : (
                            <BellSlashIcon className="w-5 h-5 text-gray-400" />
                        )}
                        <div>
                            <Label htmlFor="notifications-enabled" className="font-medium">
                                Enable Notifications
                            </Label>
                            <p className="text-xs text-muted-foreground">
                                Master switch for all notifications
                            </p>
                        </div>
                    </div>
                    <Switch
                        id="notifications-enabled"
                        checked={settings.enabled}
                        onCheckedChange={(checked) => updateSetting('enabled', checked)}
                    />
                </div>

                {/* Notification Categories */}
                {settings.enabled && (
                    <div className="space-y-4">
                        <h4 className="font-medium text-sm">Notification Categories</h4>

                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-2">
                                    <ExclamationTriangleIcon className="w-4 h-4 text-red-500" />
                                    <Label htmlFor="connection-errors" className="text-sm">
                                        Connection Errors
                                    </Label>
                                </div>
                                <Switch
                                    id="connection-errors"
                                    checked={settings.showConnectionErrors}
                                    onCheckedChange={(checked) => updateSetting('showConnectionErrors', checked)}
                                />
                            </div>

                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-2">
                                    <InformationCircleIcon className="w-4 h-4 text-blue-500" />
                                    <Label htmlFor="simulation-events" className="text-sm">
                                        Simulation Events
                                    </Label>
                                </div>
                                <Switch
                                    id="simulation-events"
                                    checked={settings.showSimulationEvents}
                                    onCheckedChange={(checked) => updateSetting('showSimulationEvents', checked)}
                                />
                            </div>

                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-2">
                                    <ExclamationTriangleIcon className="w-4 h-4 text-yellow-500" />
                                    <Label htmlFor="device-errors" className="text-sm">
                                        Device Errors
                                    </Label>
                                </div>
                                <Switch
                                    id="device-errors"
                                    checked={settings.showDeviceErrors}
                                    onCheckedChange={(checked) => updateSetting('showDeviceErrors', checked)}
                                />
                            </div>

                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-2">
                                    <InformationCircleIcon className="w-4 h-4 text-gray-500" />
                                    <Label htmlFor="retry-attempts" className="text-sm">
                                        Retry Attempts
                                    </Label>
                                </div>
                                <Switch
                                    id="retry-attempts"
                                    checked={settings.showRetryAttempts}
                                    onCheckedChange={(checked) => updateSetting('showRetryAttempts', checked)}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {/* Duration Settings */}
                {settings.enabled && (
                    <div className="space-y-4">
                        <h4 className="font-medium text-sm">Display Duration</h4>

                        <div className="space-y-4">
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <Label className="text-sm">Error Duration</Label>
                                    <Badge variant="destructive" className="text-xs">
                                        {settings.errorDuration / 1000}s
                                    </Badge>
                                </div>
                                <Slider
                                    value={[settings.errorDuration]}
                                    onValueChange={([value]) => updateSetting('errorDuration', value)}
                                    min={3000}
                                    max={15000}
                                    step={1000}
                                    className="w-full"
                                />
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <Label className="text-sm">Warning Duration</Label>
                                    <Badge variant="secondary" className="text-xs bg-yellow-100 text-yellow-800">
                                        {settings.warningDuration / 1000}s
                                    </Badge>
                                </div>
                                <Slider
                                    value={[settings.warningDuration]}
                                    onValueChange={([value]) => updateSetting('warningDuration', value)}
                                    min={2000}
                                    max={10000}
                                    step={500}
                                    className="w-full"
                                />
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <Label className="text-sm">Success Duration</Label>
                                    <Badge variant="default" className="text-xs bg-green-100 text-green-800">
                                        {settings.successDuration / 1000}s
                                    </Badge>
                                </div>
                                <Slider
                                    value={[settings.successDuration]}
                                    onValueChange={([value]) => updateSetting('successDuration', value)}
                                    min={1000}
                                    max={8000}
                                    step={500}
                                    className="w-full"
                                />
                            </div>
                        </div>
                    </div>
                )}

                {/* Advanced Settings */}
                {settings.enabled && (
                    <div className="space-y-4">
                        <h4 className="font-medium text-sm">Advanced Settings</h4>

                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <Label className="text-sm">Max Notifications</Label>
                                <Badge variant="outline" className="text-xs">
                                    {settings.maxNotifications}
                                </Badge>
                            </div>
                            <Slider
                                value={[settings.maxNotifications]}
                                onValueChange={([value]) => updateSetting('maxNotifications', value)}
                                min={1}
                                max={10}
                                step={1}
                                className="w-full"
                            />
                            <p className="text-xs text-muted-foreground mt-1">
                                Maximum number of notifications shown at once
                            </p>
                        </div>

                        <div className="flex items-center justify-between">
                            <div>
                                <Label htmlFor="sound-enabled" className="text-sm">
                                    Sound Notifications
                                </Label>
                                <p className="text-xs text-muted-foreground">
                                    Play sound for important notifications
                                </p>
                            </div>
                            <Switch
                                id="sound-enabled"
                                checked={settings.soundEnabled}
                                onCheckedChange={(checked) => updateSetting('soundEnabled', checked)}
                            />
                        </div>
                    </div>
                )}

                {/* Reset Button */}
                <div className="pt-4 border-t">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={resetToDefaults}
                        className="w-full"
                    >
                        Reset to Defaults
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
};

export default NotificationSettings;