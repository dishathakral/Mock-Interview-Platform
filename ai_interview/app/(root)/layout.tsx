import { ReactNode } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { Button } from "@/components/ui/button"
import ResumeUploadDialog from '@/components/ResumeUploadDialog'

import Navbar from '@/components/Navbar'

const rootlayout = ({ children }: { children: ReactNode }) => {
  return (
    <div className='root-layout'>
      <Navbar />
      {/* push content below fixed header */}
      <div className="pt-9" />
      {children}
    </div>
  )
}

export default rootlayout
