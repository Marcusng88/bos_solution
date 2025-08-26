"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"

export function AlertSettings() {
  return (
    <div className="space-y-6">
      {/* Alert Types */}
      <Card>
        <CardHeader>
          <CardTitle>Alert Types</CardTitle>
          <CardDescription>Configure which competitor activities trigger alerts</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">New Content Posts</Label>
              <p className="text-sm text-muted-foreground">Alert when competitors publish new content</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Pricing Changes</Label>
              <p className="text-sm text-muted-foreground">Monitor competitor pricing updates</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Ad Campaign Launches</Label>
              <p className="text-sm text-muted-foreground">Track new advertising campaigns</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Website Changes</Label>
              <p className="text-sm text-muted-foreground">Detect website updates and changes</p>
            </div>
            <Switch />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Social Media Engagement</Label>
              <p className="text-sm text-muted-foreground">Monitor unusual engagement spikes</p>
            </div>
            <Switch defaultChecked />
          </div>
        </CardContent>
      </Card>

      {/* Alert Thresholds */}
      <Card>
        <CardHeader>
          <CardTitle>Alert Thresholds</CardTitle>
          <CardDescription>Set sensitivity levels for different alert types</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label>Engagement Spike Threshold</Label>
            <div className="px-3">
              <Slider defaultValue={[50]} max={100} step={10} />
            </div>
            <p className="text-sm text-muted-foreground">Alert when engagement increases by 50% or more</p>
          </div>
          <div className="space-y-2">
            <Label>Price Change Sensitivity</Label>
            <div className="px-3">
              <Slider defaultValue={[10]} max={50} step={5} />
            </div>
            <p className="text-sm text-muted-foreground">Alert for price changes of 10% or more</p>
          </div>
          <div className="space-y-2">
            <Label>Content Volume Threshold</Label>
            <div className="px-3">
              <Slider defaultValue={[25]} max={100} step={5} />
            </div>
            <p className="text-sm text-muted-foreground">Alert when content posting increases by 25% or more</p>
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Notification Preferences</CardTitle>
          <CardDescription>Choose how and when you receive alerts</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Email Notifications</Label>
              <Select defaultValue="immediate">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="immediate">Immediate</SelectItem>
                  <SelectItem value="hourly">Hourly Digest</SelectItem>
                  <SelectItem value="daily">Daily Summary</SelectItem>
                  <SelectItem value="off">Off</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Push Notifications</Label>
              <Select defaultValue="high">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Alerts</SelectItem>
                  <SelectItem value="high">High Priority Only</SelectItem>
                  <SelectItem value="off">Off</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-2">
            <Label>Email Address</Label>
            <Input placeholder="your@email.com" defaultValue="user@company.com" />
          </div>
          <div className="space-y-2">
            <Label>Quiet Hours</Label>
            <div className="flex gap-2">
              <Select defaultValue="22">
                <SelectTrigger className="w-20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 24 }, (_, i) => (
                    <SelectItem key={i} value={i.toString()}>
                      {i.toString().padStart(2, "0")}:00
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <span className="self-center">to</span>
              <Select defaultValue="8">
                <SelectTrigger className="w-20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 24 }, (_, i) => (
                    <SelectItem key={i} value={i.toString()}>
                      {i.toString().padStart(2, "0")}:00
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button>Save Settings</Button>
      </div>
    </div>
  )
}
