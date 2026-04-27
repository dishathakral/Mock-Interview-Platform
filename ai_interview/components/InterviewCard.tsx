import React from 'react'
import dayjs from 'dayjs';
import Image from 'next/image';
import { getRandomInterviewCover } from "@/lib/utils";
import { interviewCovers } from '@/constants';
import { Button } from './ui/button';
import Link from 'next/link';

import DisplayTechIcons from './DisplayTechIcons';

interface Feedback {
  totalScore: number;
  finalAssessment: string;
  createdAt: string;
}

interface InterviewCardProps {
  interviewid: string | number;
  userId: string;
  role: string;
  type: string;
  techstack: string[];
  createdAt: string;
}

const InterviewCard = ({
  interviewid,
  userId,
  role,
  type,
  techstack,
  createdAt,
}: InterviewCardProps) => {
  const feedback = null as Feedback | null;
  const normalizedType = /mix/gi.test(type) ? 'Mixed' : type;
  const formattedDate = dayjs(feedback?.createdAt || createdAt || Date.now()).format("MMM-DD-YYYY");
  return (
    <div className="card-border w-[360px] max-sm:w-full min-h-96">
      <div className="card-interview">
        <div>
          <div className="absolute top-0 right-0 w-fit px-4 py-2 rounded-bl-lg bg-gradient-to-tr from-purple-600 to-blue-500 text-white text-sm">
            <p className="badge-text">{normalizedType}</p>
          </div>
          <Image
            src={getRandomInterviewCover()}
            alt="cover-image"
            width={90}
            height={90}
            className="rounded-full object-fit size-[60px]"
          />
          <h3 className='mt-5 capitalize text-lg'>
            {role} - {techstack.join(", ")}
          </h3>
          <div className='flex flex-row gap-5 mt-3'>
            <div className='flex flex-row gap-2'>
              <Image src="/calendar.svg" alt="calendar-icon" width={16} height={16} style={{ height: 'auto' }} />
              <p className='text-sm'>{formattedDate}</p>
            </div>
            <div className='flex flex-row gap-2 items-center'>
              <Image src="/star.svg" alt="star" width={16} height={16} style={{ height: 'auto' }} />
              <p className='text-sm'>{feedback?.totalScore || "---"}/100</p>
            </div>
          </div>
          <p className='line-clamp-2 mt-5 text-sm'>
            {feedback?.finalAssessment || "You have not completed this interview yet. Click to start practicing!"}
          </p>
        </div>
        <div className="flex flex-row justify-between items-center mt-5">
          <DisplayTechIcons techstack={techstack} />
          <Button className='btn-primary'>
            <Link href={
              feedback ? `/interview/${interviewid}/feedback` : `/interview/${interviewid}`
            }>
              {feedback ? "View Feedback" : "Start Interview"}
            </Link>
          </Button>
        </div>

      </div>

    </div>
  )
}

export default InterviewCard