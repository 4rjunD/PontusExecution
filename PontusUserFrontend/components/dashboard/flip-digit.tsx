"use client"

import { useEffect, useState, useRef } from "react"
import { cn } from "@/lib/utils"

interface FlipDigitProps {
  value: number
  decimals?: number
  className?: string
}

export function FlipDigit({ value, decimals = 4, className }: FlipDigitProps) {
  const [displayValue, setDisplayValue] = useState(value)
  const [flippingIndices, setFlippingIndices] = useState<Set<number>>(new Set())
  const prevValueRef = useRef<number | null>(null)

  useEffect(() => {
    if (prevValueRef.current === null) {
      // Initial render
      setDisplayValue(value)
      prevValueRef.current = value
      return
    }

    // Always check if value changed (even if small)
    if (Math.abs(prevValueRef.current - value) > 0.00001) {
      const oldStr = prevValueRef.current.toFixed(decimals)
      const newStr = value.toFixed(decimals)
      
      const indicesToFlip = new Set<number>()
      
      // Find which digit positions changed
      for (let i = 0; i < Math.max(oldStr.length, newStr.length); i++) {
        const oldChar = oldStr[i]
        const newChar = newStr[i]
        if (oldChar !== newChar && /[0-9]/.test(newChar || "")) {
          indicesToFlip.add(i)
        }
      }
      
      if (indicesToFlip.size > 0) {
        setFlippingIndices(indicesToFlip)
        
        // Update value after animation completes
        const timer = setTimeout(() => {
          setDisplayValue(value)
          setFlippingIndices(new Set())
          prevValueRef.current = value
        }, 300)
        
        return () => clearTimeout(timer)
      } else {
        // Value changed but digits didn't (very small change)
        prevValueRef.current = value
        setDisplayValue(value)
      }
    }
  }, [value, decimals])

  const formatted = displayValue.toFixed(decimals)
  const targetFormatted = value.toFixed(decimals)
  const chars = formatted.split("")

  return (
    <span className={cn("inline-flex items-center font-mono", className)}>
      {chars.map((char, index) => {
        const isNumber = /[0-9]/.test(char)
        const shouldFlip = isNumber && flippingIndices.has(index)
        const targetChar = targetFormatted[index] || char

        return (
          <span
            key={`${index}-${char}-${targetChar}`}
            className="inline-block relative"
            style={{
              transformStyle: "preserve-3d",
              width: isNumber ? "0.6em" : "auto",
              textAlign: isNumber ? "center" : "left",
            }}
          >
            {shouldFlip ? (
              <>
                <span className="opacity-0">{char}</span>
                <span 
                  className="absolute inset-0 inline-block animate-flip"
                  style={{
                    animationDelay: `${index * 15}ms`,
                  }}
                >
                  {targetChar}
                </span>
              </>
            ) : (
              <span>{char}</span>
            )}
          </span>
        )
      })}
    </span>
  )
}

