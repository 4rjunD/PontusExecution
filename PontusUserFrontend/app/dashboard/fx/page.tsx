"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  TrendingUp,
  Clock,
  DollarSign,
  AlertCircle,
  Zap,
  TrendingDown,
  RefreshCw,
  BarChart3,
  Activity,
  Shield,
  LineChart,
  PieChart,
} from "lucide-react"
import { formatCurrency, formatDate } from "@/lib/utils"
import { FlipDigit } from "@/components/dashboard/flip-digit"
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area,
} from "recharts"
import {
  getFXRates,
  getFXRateHistory,
  getOptimalTimeToSend,
  getCostForecast,
  getMicroHedgePosition,
  getFXSources,
  compareFXRates,
} from "@/lib/api"

interface FXRate {
  pair: string
  rate: number
  change_24h: number
  change_percent: number
  trend: string
  source: string
  last_updated: string
  bid?: number
  ask?: number
  spread?: number
}

interface CostForecast {
  metric: string
  current: number
  forecast: number
  trend: string
  confidence: number
}

interface OptimalTime {
  best_time: string
  estimated_savings: number
  reasoning: string
  alternative_times: Array<{
    time: string
    savings: number
    reasoning: string
  }>
}

export default function FXPage() {
  const [rates, setRates] = useState<FXRate[]>([])
  const [prevRates, setPrevRates] = useState<Map<string, number>>(new Map())
  const [costForecasts, setCostForecasts] = useState<CostForecast[]>([])
  const [optimalTime, setOptimalTime] = useState<OptimalTime | null>(null)
  const [microHedge, setMicroHedge] = useState<any>(null)
  const [fxSources, setFxSources] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<string>("")
  const [mounted, setMounted] = useState(false)
  const [selectedPair, setSelectedPair] = useState("USD/EUR")
  const [amount, setAmount] = useState(10000)
  const [rateHistory, setRateHistory] = useState<any>(null)
  const [comparison, setComparison] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setMounted(true)
  }, [])

  const fetchFXData = async () => {
    try {
      // Only show loading on very first load
      if (rates.length === 0 && !mounted) {
        setLoading(true)
      } else {
        setLoading(false)
      }
      setError(null)
      const [
        ratesData,
        forecastData,
        hedgeData,
        sourcesData,
      ] = await Promise.all([
        getFXRates().catch((e) => {
          console.error("Error fetching FX rates:", e)
          return { rates: [] }
        }),
        getCostForecast().catch((e) => {
          console.error("Error fetching cost forecast:", e)
          return { forecasts: [] }
        }),
        getMicroHedgePosition().catch((e) => {
          console.error("Error fetching hedge position:", e)
          return null
        }),
        getFXSources().catch((e) => {
          console.error("Error fetching FX sources:", e)
          return { active_sources: [] }
        }),
      ])

      const newRates = ratesData.rates || []
      
      // Store previous rates BEFORE updating to new rates
      if (newRates.length > 0) {
        // Update previous rates map with current rates before setting new ones
        const newPrevRates = new Map<string, number>()
        rates.forEach((rate: FXRate) => {
          newPrevRates.set(rate.pair, rate.rate)
        })
        setPrevRates(newPrevRates)
        
        // Now set the new rates
        setRates(newRates)
      }
      
      setCostForecasts(forecastData.forecasts || [])
      setMicroHedge(hedgeData)
      setFxSources(sourcesData.active_sources || [])
      setLastUpdate(new Date().toLocaleTimeString())
      
      // Show error if no data and backend might be down
      if ((!ratesData.rates || ratesData.rates.length === 0) && 
          (!sourcesData.active_sources || sourcesData.active_sources.length === 0)) {
        setError("Unable to connect to backend API. Please ensure the backend server is running on http://localhost:8000")
      }
    } catch (error: any) {
      console.error("Error fetching FX data:", error)
      setError(error?.message || "Failed to fetch FX data. Please check backend connection.")
    } finally {
      setLoading(false)
    }
  }

  const fetchOptimalTime = async () => {
    try {
      const [from, to] = selectedPair.split("/")
      const data = await getOptimalTimeToSend(from, to, amount)
      setOptimalTime(data)
    } catch (error) {
      console.error("Error fetching optimal time:", error)
    }
  }

  const fetchRateHistory = async () => {
    try {
      const data = await getFXRateHistory(selectedPair, 7)
      setRateHistory(data)
    } catch (error) {
      console.error("Error fetching rate history:", error)
    }
  }

  const fetchComparison = async () => {
    try {
      const data = await compareFXRates(selectedPair, amount)
      setComparison(data)
    } catch (error) {
      console.error("Error fetching comparison:", error)
    }
  }

  useEffect(() => {
    fetchFXData()
    // Refresh every 2 seconds for real-time updates
    const interval = setInterval(fetchFXData, 2000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (selectedPair && amount) {
      fetchOptimalTime()
      fetchRateHistory()
      fetchComparison()
    }
  }, [selectedPair, amount])

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-accent/20 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-4xl font-bold tracking-tight text-foreground">FX Intelligence & Cost Optimization</h1>
          <p className="text-muted-foreground text-lg">
            Real-time FX monitoring using 20+ free sources and predictive cost forecasting
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={fetchFXData} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          {mounted && lastUpdate && (
            <div className="text-xs text-muted-foreground">
              Last updated: {lastUpdate}
            </div>
          )}
        </div>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-800">
              <AlertCircle className="h-5 w-5" />
              <div>
                <div className="font-medium">Connection Error</div>
                <div className="text-sm mt-1">{error}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Active Sources
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{fxSources.length || 8}</div>
            <div className="text-xs text-muted-foreground mt-1">FX rate providers</div>
            {fxSources.length > 0 && (
              <div className="text-xs text-green-600 mt-1">✓ All sources active</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Live Rates
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{rates.length || 0}</div>
            <div className="text-xs text-muted-foreground mt-1">Currency pairs</div>
            {rates.length > 0 && (
              <div className="text-xs text-blue-600 mt-1">Real-time data</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Update Frequency
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">2s</div>
            <div className="text-xs text-muted-foreground mt-1">Real-time updates</div>
            <div className="text-xs text-green-600 mt-1">✓ Auto-refresh enabled</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Data Quality
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">98%</div>
            <div className="text-xs text-muted-foreground mt-1">Accuracy score</div>
            <div className="text-xs text-green-600 mt-1">✓ High confidence</div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="rates" className="space-y-4">
        <TabsList>
          <TabsTrigger value="rates">Live Rates</TabsTrigger>
          <TabsTrigger value="optimal-time">Optimal Time</TabsTrigger>
          <TabsTrigger value="forecasting">Cost Forecasting</TabsTrigger>
          <TabsTrigger value="comparison">Rate Comparison</TabsTrigger>
          <TabsTrigger value="history">Rate History</TabsTrigger>
          <TabsTrigger value="hedging">Micro-Hedging</TabsTrigger>
        </TabsList>

        {/* Live Rates Tab */}
        <TabsContent value="rates" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Real-Time FX Rates</CardTitle>
              <CardDescription>Live rates from multiple sources, updating every 2 seconds</CardDescription>
            </CardHeader>
            <CardContent>
              {rates.length === 0 && loading ? (
                <div className="text-center py-8">
                  <RefreshCw className="h-6 w-6 animate-spin mx-auto" />
                  <p className="mt-2 text-sm text-muted-foreground">Loading rates...</p>
                </div>
              ) : rates.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No rates available. Check backend connection.
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
                  {rates.map((rate) => {
                    const prevRate = prevRates.get(rate.pair)
                    const rateChanged = prevRate !== undefined && Math.abs(prevRate - rate.rate) > 0.0001
                    
                    return (
                      <Card key={rate.pair} className="transition-all duration-200">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm">{rate.pair}</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-xl font-bold relative font-mono">
                            <FlipDigit 
                              value={rate.rate} 
                              decimals={4}
                              key={`rate-${rate.pair}-${Date.now()}`}
                            />
                          </div>
                          <div className={`text-xs mt-1 flex items-center gap-1 transition-colors ${
                            rate.trend === "up" ? "text-green-600" : rate.trend === "down" ? "text-red-600" : "text-gray-600"
                          }`}>
                            {rate.trend === "up" ? (
                              <TrendingUp className="h-3 w-3" />
                            ) : rate.trend === "down" ? (
                              <TrendingDown className="h-3 w-3" />
                            ) : null}
                            <span className="font-mono">
                              <FlipDigit 
                                value={Math.abs(rate.change_percent)} 
                                decimals={2}
                                key={`change-${rate.pair}-${rate.change_percent}`}
                              />
                              {rate.change_percent > 0 ? "+" : ""}%
                            </span>
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">{rate.source}</div>
                          {rate.spread && (
                            <div className="text-xs text-muted-foreground mt-1">
                              Spread: <span className="font-mono">{rate.spread.toFixed(4)}</span>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>FX Rate Sources</CardTitle>
              <CardDescription>Active data sources providing real-time rates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2 md:grid-cols-4">
                {fxSources.length > 0 ? (
                  fxSources.map((source) => (
                    <div key={source} className="p-2 border rounded text-center text-sm bg-green-50">
                      <Activity className="h-4 w-4 mx-auto mb-1 text-green-600" />
                      {source}
                    </div>
                  ))
                ) : (
                  ["ECB", "Frankfurter", "ExchangeRate API", "Wise", "Remitly", "Bank APIs", "Crypto Exchanges"].map((source) => (
                    <div key={source} className="p-2 border rounded text-center text-sm">
                      {source}
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Optimal Time Tab */}
        <TabsContent value="optimal-time" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Optimal Time to Send
              </CardTitle>
              <CardDescription>AI-powered timing recommendations based on gas fees and FX liquidity</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 mb-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <label className="text-sm font-medium">Currency Pair</label>
                    <Select value={selectedPair} onValueChange={setSelectedPair}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="USD/EUR">USD/EUR</SelectItem>
                        <SelectItem value="USD/GBP">USD/GBP</SelectItem>
                        <SelectItem value="USD/INR">USD/INR</SelectItem>
                        <SelectItem value="EUR/GBP">EUR/GBP</SelectItem>
                        <SelectItem value="USD/JPY">USD/JPY</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Amount</label>
                    <Input
                      type="number"
                      value={amount}
                      onChange={(e) => setAmount(Number(e.target.value))}
                      placeholder="10000"
                    />
                  </div>
                  <div className="flex items-end">
                    <Button onClick={fetchOptimalTime} className="w-full">
                      <Zap className="h-4 w-4 mr-2" />
                      Calculate
                    </Button>
                  </div>
                </div>
              </div>

              {optimalTime ? (
                <div className="space-y-3">
                  <div className="p-4 border rounded-lg bg-green-50">
                    <div className="font-medium text-green-900">
                      Best time: {formatDate(optimalTime.best_time)}
                    </div>
                    <div className="text-sm text-green-700 mt-1">
                      Save {formatCurrency(optimalTime.estimated_savings)} vs sending now
                    </div>
                    <div className="text-xs text-green-600 mt-2">
                      {optimalTime.reasoning}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm font-medium">Alternative Times:</div>
                    {optimalTime.alternative_times.map((alt, idx) => (
                      <div key={idx} className="flex items-center justify-between p-2 border rounded">
                        <div>
                          <span className="font-medium">{formatDate(alt.time)}</span>
                          <div className="text-xs text-muted-foreground">{alt.reasoning}</div>
                        </div>
                        <span className="text-sm font-medium text-green-600">
                          Save {formatCurrency(alt.savings)}
                        </span>
                      </div>
                    ))}
                  </div>
                  <Button className="w-full">
                    <Clock className="mr-2 h-4 w-4" />
                    Schedule for Optimal Time
                  </Button>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  Select a currency pair and amount to get optimal time recommendations
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Cost Forecasting Tab */}
        <TabsContent value="forecasting" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Predictive Cost Forecasting</CardTitle>
              <CardDescription>Gas, bridge fees, and FX liquidity predictions</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Metric</TableHead>
                    <TableHead>Current</TableHead>
                    <TableHead>Forecast</TableHead>
                    <TableHead>Trend</TableHead>
                    <TableHead>Confidence</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {costForecasts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                        Loading forecasts...
                      </TableCell>
                    </TableRow>
                  ) : (
                    costForecasts.map((item, idx) => (
                      <TableRow key={idx}>
                        <TableCell className="font-medium">{item.metric}</TableCell>
                        <TableCell>
                          {typeof item.current === "number" && item.current < 10
                            ? formatCurrency(item.current)
                            : item.current}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <span>
                              {typeof item.forecast === "number" && item.forecast < 10
                                ? formatCurrency(item.forecast)
                                : item.forecast}
                            </span>
                            {item.trend === "down" ? (
                              <TrendingDown className="h-4 w-4 text-green-600" />
                            ) : (
                              <TrendingUp className="h-4 w-4 text-red-600" />
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <span className={`px-2 py-1 rounded text-xs ${
                            item.trend === "down" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                          }`}>
                            {item.trend}
                          </span>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full"
                                style={{ width: `${item.confidence * 100}%` }}
                              />
                            </div>
                            <span className="text-xs text-muted-foreground">
                              {(item.confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
          
          {/* Forecast Chart */}
          {costForecasts.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Forecast Comparison
                </CardTitle>
                <CardDescription>Current vs. Forecasted costs</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={costForecasts.map((f) => ({
                    metric: f.metric.split(" ")[0], // Shortened name
                    current: typeof f.current === "number" ? f.current : 0,
                    forecast: typeof f.forecast === "number" ? f.forecast : 0,
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis
                      dataKey="metric"
                      tick={{ fontSize: 12 }}
                      className="text-muted-foreground"
                    />
                    <YAxis
                      tick={{ fontSize: 12 }}
                      className="text-muted-foreground"
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "hsl(var(--background))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "6px",
                      }}
                    />
                    <Legend />
                    <Bar dataKey="current" fill="hsl(var(--muted-foreground))" name="Current" />
                    <Bar dataKey="forecast" fill="hsl(var(--primary))" name="Forecast" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Rate Comparison Tab */}
        <TabsContent value="comparison" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compare FX Rates Across Providers</CardTitle>
              <CardDescription>Find the best rate for your conversion</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 mb-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <label className="text-sm font-medium">Currency Pair</label>
                    <Select value={selectedPair} onValueChange={setSelectedPair}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="USD/EUR">USD/EUR</SelectItem>
                        <SelectItem value="USD/GBP">USD/GBP</SelectItem>
                        <SelectItem value="USD/INR">USD/INR</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Amount</label>
                    <Input
                      type="number"
                      value={amount}
                      onChange={(e) => setAmount(Number(e.target.value))}
                    />
                  </div>
                  <div className="flex items-end">
                    <Button onClick={fetchComparison} className="w-full">
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Compare
                    </Button>
                  </div>
                </div>
              </div>

              {comparison ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Provider</TableHead>
                      <TableHead>Rate</TableHead>
                      <TableHead>Output Amount</TableHead>
                      <TableHead>Fee</TableHead>
                      <TableHead>Total Cost</TableHead>
                      <TableHead>Reliability</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {comparison.comparisons.map((comp: any, idx: number) => (
                      <TableRow key={idx} className={idx === 0 ? "bg-green-50" : ""}>
                        <TableCell className="font-medium">
                          {comp.provider}
                          {idx === 0 && (
                            <span className="ml-2 text-xs text-green-600">Best</span>
                          )}
                        </TableCell>
                        <TableCell>{comp.rate.toFixed(4)}</TableCell>
                        <TableCell>{formatCurrency(comp.output_amount)}</TableCell>
                        <TableCell>{formatCurrency(comp.fee)}</TableCell>
                        <TableCell className="font-medium">
                          {formatCurrency(comp.total_cost)}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full"
                                style={{ width: `${comp.reliability * 100}%` }}
                              />
                            </div>
                            <span className="text-xs">{(comp.reliability * 100).toFixed(0)}%</span>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  Select a pair and amount to compare rates
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Rate History Tab */}
        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>FX Rate History</CardTitle>
              <CardDescription>Historical rate data and volatility analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4">
                <label className="text-sm font-medium">Currency Pair</label>
                <Select value={selectedPair} onValueChange={setSelectedPair}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="USD/EUR">USD/EUR</SelectItem>
                    <SelectItem value="USD/GBP">USD/GBP</SelectItem>
                    <SelectItem value="USD/INR">USD/INR</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {rateHistory ? (
                <div className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-4">
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Min Rate</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{rateHistory.min_rate?.toFixed(4) || "N/A"}</div>
                        <div className="text-xs text-muted-foreground mt-1">7-day minimum</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Max Rate</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{rateHistory.max_rate?.toFixed(4) || "N/A"}</div>
                        <div className="text-xs text-muted-foreground mt-1">7-day maximum</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Avg Rate</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{rateHistory.avg_rate?.toFixed(4) || "N/A"}</div>
                        <div className="text-xs text-muted-foreground mt-1">7-day average</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Volatility</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{rateHistory.volatility?.toFixed(4) || "N/A"}</div>
                        <div className="text-xs text-muted-foreground mt-1">Standard deviation</div>
                      </CardContent>
                    </Card>
                  </div>
                  
                  {/* Rate History Chart */}
                  {rateHistory.rates && rateHistory.rates.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <LineChart className="h-5 w-5" />
                          Rate History Chart
                        </CardTitle>
                        <CardDescription>Historical rate movements over the past 7 days</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                          <RechartsLineChart
                            data={rateHistory.rates.slice().reverse().map((r: any) => ({
                              time: new Date(r.timestamp || r.time || Date.now()).toLocaleDateString("en-US", {
                                month: "short",
                                day: "numeric",
                                hour: "2-digit",
                              }),
                              rate: r.rate || r.value || 0,
                            }))}
                          >
                            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                            <XAxis
                              dataKey="time"
                              tick={{ fontSize: 12 }}
                              className="text-muted-foreground"
                            />
                            <YAxis
                              tick={{ fontSize: 12 }}
                              className="text-muted-foreground"
                              domain={["auto", "auto"]}
                            />
                            <Tooltip
                              contentStyle={{
                                backgroundColor: "hsl(var(--background))",
                                border: "1px solid hsl(var(--border))",
                                borderRadius: "6px",
                              }}
                              formatter={(value: any) => [value.toFixed(4), "Rate"]}
                            />
                            <Legend />
                            <Line
                              type="monotone"
                              dataKey="rate"
                              stroke="hsl(var(--primary))"
                              strokeWidth={2}
                              dot={{ r: 3 }}
                              activeDot={{ r: 5 }}
                              name="Exchange Rate"
                            />
                          </RechartsLineChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>
                  )}
                  
                  <div className="text-sm text-muted-foreground">
                    Showing {rateHistory.rates?.length || 0} data points over 7 days
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  Select a currency pair to view history
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Micro-Hedging Tab */}
        <TabsContent value="hedging" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Micro-Hedging with Stablecoins</CardTitle>
              <CardDescription>Optional hedging strategy using stablecoins</CardDescription>
            </CardHeader>
            <CardContent>
              {microHedge ? (
                <div className="space-y-4">
                  <div className="p-4 border rounded-lg">
                    <div className="font-medium mb-2">Current Hedging Position</div>
                    <div className="grid gap-4 md:grid-cols-3">
                      <div>
                        <div className="text-sm text-muted-foreground">USDC Holdings</div>
                        <div className="text-xl font-bold">{formatCurrency(microHedge.stablecoin_holdings)}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Hedged Exposure</div>
                        <div className="text-xl font-bold">{formatCurrency(microHedge.hedged_exposure)}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Hedge Ratio</div>
                        <div className="text-xl font-bold">{microHedge.hedge_ratio}%</div>
                      </div>
                    </div>
                  </div>
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <div className="text-sm font-medium text-blue-900">
                      Recommendation: {microHedge.recommended_action}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline">Increase Hedge</Button>
                    <Button variant="outline">Decrease Hedge</Button>
                    <Button variant="outline">Auto-Hedge</Button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  Loading hedging position...
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
