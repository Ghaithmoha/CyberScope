import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Activity, 
  AlertTriangle, 
  BarChart3, 
  Database, 
  Eye, 
  Filter, 
  Search, 
  Settings, 
  Shield, 
  TrendingUp,
  Bell,
  Download,
  RefreshCw,
  Calendar,
  Clock,
  Server,
  Users,
  Zap
} from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import './App.css'

// Mock data for demonstration
const mockLogData = [
  { time: '00:00', INFO: 120, WARNING: 15, ERROR: 3, DEBUG: 45 },
  { time: '04:00', INFO: 98, WARNING: 12, ERROR: 1, DEBUG: 32 },
  { time: '08:00', INFO: 180, WARNING: 25, ERROR: 8, DEBUG: 67 },
  { time: '12:00', INFO: 220, WARNING: 35, ERROR: 12, DEBUG: 89 },
  { time: '16:00', INFO: 195, WARNING: 28, ERROR: 6, DEBUG: 78 },
  { time: '20:00', INFO: 165, WARNING: 22, ERROR: 4, DEBUG: 56 }
]

const mockAnomalies = [
  { id: 1, timestamp: '2025-06-17 14:23:45', level: 'ERROR', source: 'payment_gateway', message: 'Payment processing failed for order order_12345: Connection timeout', score: 0.95 },
  { id: 2, timestamp: '2025-06-17 14:18:32', level: 'WARNING', source: 'auth_service', message: 'Unusual login pattern detected from IP 192.168.1.100', score: 0.87 },
  { id: 3, timestamp: '2025-06-17 14:15:21', level: 'ERROR', source: 'database', message: 'Database connection pool exhausted', score: 0.92 },
  { id: 4, timestamp: '2025-06-17 14:12:10', level: 'WARNING', source: 'web_server', message: 'High memory usage detected: 95% on server srv_3', score: 0.78 }
]

const mockRecentLogs = [
  { id: 1, timestamp: '2025-06-17 14:30:15', level: 'INFO', source: 'web_server', message: 'User user_8773 logged in successfully from IP 107.6.148.100' },
  { id: 2, timestamp: '2025-06-17 14:30:12', level: 'DEBUG', source: 'auth_service', message: 'Processing request req_789456 from user user_8773' },
  { id: 3, timestamp: '2025-06-17 14:30:08', level: 'WARNING', source: 'database', message: 'Slow query detected: 2500ms for query q_4567' },
  { id: 4, timestamp: '2025-06-17 14:30:05', level: 'INFO', source: 'file_system', message: 'File document_456.pdf uploaded successfully by user user_8773' },
  { id: 5, timestamp: '2025-06-17 14:30:02', level: 'ERROR', source: 'payment_gateway', message: 'Payment processing failed for order order_67890: Invalid credentials' }
]

const sourceDistribution = [
  { name: 'Web Server', value: 35, color: '#8884d8' },
  { name: 'Database', value: 25, color: '#82ca9d' },
  { name: 'Auth Service', value: 20, color: '#ffc658' },
  { name: 'Payment Gateway', value: 15, color: '#ff7300' },
  { name: 'File System', value: 5, color: '#00ff88' }
]

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff88']

function Dashboard() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedLevel, setSelectedLevel] = useState('all')
  const [selectedSource, setSelectedSource] = useState('all')
  const [isRealTime, setIsRealTime] = useState(true)

  const getLevelColor = (level) => {
    switch (level) {
      case 'ERROR': return 'bg-red-500'
      case 'WARNING': return 'bg-yellow-500'
      case 'INFO': return 'bg-blue-500'
      case 'DEBUG': return 'bg-gray-500'
      default: return 'bg-gray-500'
    }
  }

  const getLevelBadgeVariant = (level) => {
    switch (level) {
      case 'ERROR': return 'destructive'
      case 'WARNING': return 'secondary'
      case 'INFO': return 'default'
      case 'DEBUG': return 'outline'
      default: return 'outline'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Activity className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  LogAnalyzer Pro
                </h1>
              </div>
              <Badge variant="secondary" className="ml-4">
                Enterprise Edition
              </Badge>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-400">
                <div className={`w-2 h-2 rounded-full ${isRealTime ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                <span>{isRealTime ? 'Real-time' : 'Offline'}</span>
              </div>
              <Button variant="outline" size="sm">
                <Bell className="w-4 h-4 mr-2" />
                Alerts
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white border-0">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100 text-sm font-medium">Total Logs Today</p>
                    <p className="text-3xl font-bold">1,247,892</p>
                    <p className="text-blue-100 text-sm">+12.5% from yesterday</p>
                  </div>
                  <Database className="w-8 h-8 text-blue-200" />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="bg-gradient-to-r from-red-500 to-red-600 text-white border-0">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-red-100 text-sm font-medium">Critical Errors</p>
                    <p className="text-3xl font-bold">23</p>
                    <p className="text-red-100 text-sm">-8.2% from yesterday</p>
                  </div>
                  <AlertTriangle className="w-8 h-8 text-red-200" />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white border-0">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-yellow-100 text-sm font-medium">Anomalies Detected</p>
                    <p className="text-3xl font-bold">156</p>
                    <p className="text-yellow-100 text-sm">+3.1% from yesterday</p>
                  </div>
                  <Shield className="w-8 h-8 text-yellow-200" />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white border-0">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-100 text-sm font-medium">System Health</p>
                    <p className="text-3xl font-bold">98.7%</p>
                    <p className="text-green-100 text-sm">+0.3% from yesterday</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-200" />
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Charts */}
          <div className="lg:col-span-2 space-y-8">
            {/* Log Trends Chart */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <BarChart3 className="w-5 h-5" />
                    <span>Log Trends (Last 24 Hours)</span>
                  </CardTitle>
                  <CardDescription>
                    Real-time log volume and distribution by severity level
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={mockLogData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Area type="monotone" dataKey="ERROR" stackId="1" stroke="#ef4444" fill="#ef4444" />
                      <Area type="monotone" dataKey="WARNING" stackId="1" stroke="#f59e0b" fill="#f59e0b" />
                      <Area type="monotone" dataKey="INFO" stackId="1" stroke="#3b82f6" fill="#3b82f6" />
                      <Area type="monotone" dataKey="DEBUG" stackId="1" stroke="#6b7280" fill="#6b7280" />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>

            {/* Source Distribution */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Server className="w-5 h-5" />
                    <span>Log Sources Distribution</span>
                  </CardTitle>
                  <CardDescription>
                    Distribution of logs across different system components
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={sourceDistribution}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {sourceDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Right Column - Anomalies and Recent Logs */}
          <div className="space-y-8">
            {/* Anomalies */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Zap className="w-5 h-5 text-yellow-500" />
                    <span>Recent Anomalies</span>
                  </CardTitle>
                  <CardDescription>
                    AI-detected anomalous patterns in your logs
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {mockAnomalies.map((anomaly) => (
                    <div key={anomaly.id} className="p-4 border rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                      <div className="flex items-start justify-between mb-2">
                        <Badge variant={getLevelBadgeVariant(anomaly.level)}>
                          {anomaly.level}
                        </Badge>
                        <span className="text-xs text-slate-500">
                          Score: {anomaly.score}
                        </span>
                      </div>
                      <p className="text-sm font-medium mb-1">{anomaly.source}</p>
                      <p className="text-xs text-slate-600 dark:text-slate-400 mb-2">
                        {anomaly.message}
                      </p>
                      <div className="flex items-center text-xs text-slate-500">
                        <Clock className="w-3 h-3 mr-1" />
                        {anomaly.timestamp}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </motion.div>

            {/* Recent Logs */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.8 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Eye className="w-5 h-5" />
                    <span>Recent Logs</span>
                  </CardTitle>
                  <CardDescription>
                    Latest log entries from your systems
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {mockRecentLogs.map((log) => (
                    <div key={log.id} className="flex items-start space-x-3 p-3 border rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                      <div className={`w-2 h-2 rounded-full mt-2 ${getLevelColor(log.level)}`}></div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <Badge variant={getLevelBadgeVariant(log.level)} className="text-xs">
                            {log.level}
                          </Badge>
                          <span className="text-xs text-slate-500">{log.source}</span>
                        </div>
                        <p className="text-sm text-slate-700 dark:text-slate-300 truncate">
                          {log.message}
                        </p>
                        <div className="flex items-center text-xs text-slate-500 mt-1">
                          <Clock className="w-3 h-3 mr-1" />
                          {log.timestamp}
                        </div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>

        {/* Search and Filter Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="mt-8"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Search className="w-5 h-5" />
                <span>Advanced Log Search</span>
              </CardTitle>
              <CardDescription>
                Search and filter through millions of log entries with AI-powered insights
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col md:flex-row gap-4 mb-6">
                <div className="flex-1">
                  <Input
                    placeholder="Search logs... (e.g., 'payment failed', 'user_12345', 'error 500')"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                <Select value={selectedLevel} onValueChange={setSelectedLevel}>
                  <SelectTrigger className="w-full md:w-40">
                    <SelectValue placeholder="Log Level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Levels</SelectItem>
                    <SelectItem value="error">ERROR</SelectItem>
                    <SelectItem value="warning">WARNING</SelectItem>
                    <SelectItem value="info">INFO</SelectItem>
                    <SelectItem value="debug">DEBUG</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={selectedSource} onValueChange={setSelectedSource}>
                  <SelectTrigger className="w-full md:w-40">
                    <SelectValue placeholder="Source" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Sources</SelectItem>
                    <SelectItem value="web_server">Web Server</SelectItem>
                    <SelectItem value="database">Database</SelectItem>
                    <SelectItem value="auth_service">Auth Service</SelectItem>
                    <SelectItem value="payment_gateway">Payment Gateway</SelectItem>
                    <SelectItem value="file_system">File System</SelectItem>
                  </SelectContent>
                </Select>
                <Button className="w-full md:w-auto">
                  <Search className="w-4 h-4 mr-2" />
                  Search
                </Button>
              </div>
              
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" size="sm">
                  <Filter className="w-4 h-4 mr-2" />
                  Advanced Filters
                </Button>
                <Button variant="outline" size="sm">
                  <Calendar className="w-4 h-4 mr-2" />
                  Date Range
                </Button>
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Export Results
                </Button>
                <Button variant="outline" size="sm">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
      </Routes>
    </Router>
  )
}

export default App

