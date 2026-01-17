import { useEffect, useState } from 'react'

interface UseVoiceCommandOptions {
  onResult?: (transcript: string) => void
  onEnd?: () => void
  onError?: (error: any) => void
}

export function useVoiceCommand({ onResult, onEnd, onError }: UseVoiceCommandOptions = {}) {
  const [hasRecognitionSupport, setHasRecognitionSupport] = useState(false)
  const [recognition, setRecognition] = useState<any>(null)

  useEffect(() => {
    // Check if browser supports speech recognition
    if (typeof window !== 'undefined') {
      const SpeechRecognition = 
        (window as any).SpeechRecognition || 
        (window as any).webkitSpeechRecognition

      if (SpeechRecognition) {
        setHasRecognitionSupport(true)
        const recognitionInstance = new SpeechRecognition()
        
        recognitionInstance.continuous = false
        recognitionInstance.interimResults = false
        recognitionInstance.lang = 'en-US'

        recognitionInstance.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript
          if (onResult) {
            onResult(transcript)
          }
        }

        recognitionInstance.onend = () => {
          if (onEnd) {
            onEnd()
          }
        }

        recognitionInstance.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error)
          if (onError) {
            onError(event.error)
          }
        }

        setRecognition(recognitionInstance)
      }
    }
  }, []) // Remove dependencies to prevent infinite loop

  const startListening = () => {
    if (recognition) {
      try {
        recognition.start()
      } catch (error) {
        console.error('Error starting recognition:', error)
      }
    }
  }

  const stopListening = () => {
    if (recognition) {
      try {
        recognition.stop()
      } catch (error) {
        console.error('Error stopping recognition:', error)
      }
    }
  }

  return {
    hasRecognitionSupport,
    startListening,
    stopListening,
  }
}
