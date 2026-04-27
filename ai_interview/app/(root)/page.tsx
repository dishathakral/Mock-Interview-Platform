
"use client";

import React, { useEffect, useState } from 'react'
import Image from "next/image";
import { Button } from "@/components/ui/button";
import InterviewCard from '@/components/InterviewCard';
import { supabase } from '@/lib/supabase';
import ResumeUploadDialog from '@/components/ResumeUploadDialog';
import { Loader2 } from 'lucide-react';

export default function Home() {
  const [interviews, setInterviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadInterviews() {
      try {
        const { data, error } = await supabase
          .from("interviews")
          .select("*")
          .order("created_at", { ascending: false });

        if (error) {
          console.error("Error loading interviews:", error);
        } else {
          setInterviews(data || []);
        }
      } catch (err) {
        console.error("Failed to fetch interviews", err);
      } finally {
        setLoading(false);
      }
    }

    loadInterviews();
  }, []);

  return (
    <>
      <section className="card-cta">
        <div className="flex flex-col gap-6 max-w-lg">
          <h2>Your Smartest Interview Coach — Anytime, Anywhere.</h2>
          <p className="text-lg">
            Practice real interview questions & get instant feedback reports
          </p>

          <ResumeUploadDialog trigger={
            <Button className="btn-primary max-sm:w-full">
              Start an Interview
            </Button>
          } />
        </div>

        <Image
          src="/Chatlayer-removebg-preview.png"
          alt="Interview Illustration"
          width={300}
          height={300}
          className="max-sm:hidden"
        />
      </section>

      <section className="flex flex-col gap-6 mt-8">
        <h2>Your Interviews</h2>
        <div className="interviews-section">
          {loading ? (
            <div className="flex w-full justify-center py-10">
              <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
            </div>
          ) : interviews.length === 0 ? (
            <p className="text-zinc-400">No interviews found. Start one above!</p>
          ) : (
            interviews.map((interview) => (
              <InterviewCard
                key={interview.id}
                interviewid={interview.id}
                userId={interview.created_by}
                role={interview.role}
                type={interview.interview_type}
                techstack={[interview.role]} // Placeholder
                createdAt={interview.created_at}
              />
            ))
          )}
        </div>
      </section>
    </>
  );
}
