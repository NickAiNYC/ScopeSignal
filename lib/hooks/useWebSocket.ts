import { useEffect, useState } from 'react'
import { getWebSocketService } from '@/lib/websocket/websocketService'

interface UseWebSocketOptions {
  url?: string
  autoConnect?: boolean
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const { url = 'ws://localhost:8080', autoConnect = true } = options
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<any>(null)

  useEffect(() => {
    if (!autoConnect) return

    const wsService = getWebSocketService()
    
    // Connect to WebSocket
    wsService.connect(url)

    // Subscribe to messages
    const unsubscribe = wsService.subscribe((data) => {
      setLastMessage(data)
    })

    // Check connection status periodically
    const interval = setInterval(() => {
      setIsConnected(wsService.isConnected)
    }, 1000)

    return () => {
      unsubscribe()
      clearInterval(interval)
      // Don't disconnect here to maintain connection across component unmounts
    }
  }, [url, autoConnect])

  const send = (data: any) => {
    const wsService = getWebSocketService()
    wsService.send(data)
  }

  return {
    isConnected,
    lastMessage,
    send,
  }
}
