'use client'

import { useRef, useEffect } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Sphere, Box } from '@react-three/drei'
import * as THREE from 'three'

interface DataPoint {
  id: string
  location: string
  classification: string
  confidence: number
}

interface ThreeVisualizationProps {
  data: DataPoint[]
}

function DataPoints({ data }: { data: DataPoint[] }) {
  return (
    <group>
      {data.map((point, index) => {
        const x = (Math.random() - 0.5) * 10
        const y = (Math.random() - 0.5) * 10
        const z = (Math.random() - 0.5) * 10
        
        const color = 
          point.classification === 'CONTESTABLE' ? '#4ade80' :
          point.classification === 'SOFT_OPEN' ? '#facc15' :
          '#ef4444'

        return (
          <AnimatedSphere
            key={point.id}
            position={[x, y, z]}
            color={color}
            confidence={point.confidence}
          />
        )
      })}
    </group>
  )
}

function AnimatedSphere({ position, color, confidence }: { position: [number, number, number], color: string, confidence: number }) {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.5
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.3
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime + position[0]) * 0.5
    }
  })

  const scale = (confidence / 100) * 0.5 + 0.3

  return (
    <mesh ref={meshRef} position={position}>
      <sphereGeometry args={[scale, 16, 16]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} />
    </mesh>
  )
}

function GridPlane() {
  return (
    <gridHelper args={[20, 20, '#334155', '#1e293b']} />
  )
}

export default function ThreeVisualization({ data }: ThreeVisualizationProps) {
  return (
    <Canvas camera={{ position: [0, 5, 15], fov: 50 }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <DataPoints data={data} />
      <GridPlane />
      <OrbitControls enableZoom={true} enablePan={true} />
    </Canvas>
  )
}
