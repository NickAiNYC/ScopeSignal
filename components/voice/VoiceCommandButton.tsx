'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Mic, MicOff } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useVoiceCommand } from '@/lib/hooks/useVoiceCommand'

export default function VoiceCommandButton() {
  const router = useRouter()
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [feedback, setFeedback] = useState('')

  const handleVoiceCommand = (command: string) => {
    const lowerCommand = command.toLowerCase()
    
    // Route to different modules based on voice command
    if (lowerCommand.includes('violation') || lowerCommand.includes('compliance')) {
      setFeedback('Navigating to ViolationSentinel...')
      setTimeout(() => router.push('/violation-sentinel'), 500)
    } else if (lowerCommand.includes('healthcare') || lowerCommand.includes('regula') || lowerCommand.includes('revenue')) {
      setFeedback('Navigating to Regula...')
      setTimeout(() => router.push('/regula'), 500)
    } else if (lowerCommand.includes('ai') || lowerCommand.includes('pulse') || lowerCommand.includes('intelligence')) {
      setFeedback('Navigating to AI-PulsePoint...')
      setTimeout(() => router.push('/ai-pulsepoint'), 500)
    } else if (lowerCommand.includes('construction') || lowerCommand.includes('scope') || lowerCommand.includes('opportunity')) {
      setFeedback('Navigating to ScopeSignal...')
      setTimeout(() => router.push('/scopesignal'), 500)
    } else if (lowerCommand.includes('home') || lowerCommand.includes('dashboard')) {
      setFeedback('Returning to dashboard...')
      setTimeout(() => router.push('/'), 500)
    } else {
      setFeedback('Command not recognized. Try: "Show me healthcare violations" or "Open ScopeSignal"')
    }

    setTimeout(() => {
      setFeedback('')
      setTranscript('')
    }, 3000)
  }

  const { startListening, stopListening, hasRecognitionSupport } = useVoiceCommand({
    onResult: (result) => {
      setTranscript(result)
      if (result) {
        handleVoiceCommand(result)
      }
    },
    onEnd: () => {
      setIsListening(false)
    },
  })

  const toggleListening = () => {
    if (isListening) {
      stopListening()
      setIsListening(false)
    } else {
      startListening()
      setIsListening(true)
      setFeedback('Listening...')
    }
  }

  if (!hasRecognitionSupport) {
    return null // Hide button if voice recognition is not supported
  }

  return (
    <div className="fixed bottom-8 right-8 z-50">
      <div className="flex flex-col items-end space-y-4">
        {/* Feedback/Transcript Display */}
        <AnimatePresence>
          {(transcript || feedback) && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="glass rounded-lg p-4 max-w-sm"
            >
              {feedback && (
                <p className="text-sm text-blue-400 mb-2">{feedback}</p>
              )}
              {transcript && (
                <p className="text-sm text-slate-300">"{transcript}"</p>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Voice Command Button */}
        <motion.button
          onClick={toggleListening}
          className={`w-16 h-16 rounded-full flex items-center justify-center shadow-lg transition-all ${
            isListening
              ? 'bg-red-500 hover:bg-red-600'
              : 'bg-blue-500 hover:bg-blue-600'
          }`}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          animate={isListening ? { 
            boxShadow: ['0 0 0 0 rgba(59, 130, 246, 0.7)', '0 0 0 20px rgba(59, 130, 246, 0)'],
          } : {}}
          transition={isListening ? {
            boxShadow: {
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeOut',
            }
          } : {}}
        >
          {isListening ? (
            <MicOff className="w-8 h-8 text-white" />
          ) : (
            <Mic className="w-8 h-8 text-white" />
          )}
        </motion.button>

        {/* Help Text */}
        <motion.p
          className="text-xs text-slate-400 text-right"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          Say "Hey Command" to activate
        </motion.p>
      </div>
    </div>
  )
}
