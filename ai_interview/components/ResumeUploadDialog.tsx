
"use client";

import { useRef, useState, DragEvent } from "react";
import { useRouter } from "next/navigation";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogTrigger, DialogClose } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Upload, FileText, X, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { supabase } from "@/lib/supabase";

type Props = {
  trigger: React.ReactNode;
};

export default function ResumeUploadDialog({ trigger }: Props) {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [role, setRole] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) setFile(f);
  };

  const onDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(true);
  };

  const onDragLeave = () => setDragging(false);

  const onBrowseClick = () => fileInputRef.current?.click();

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] || null;
    setFile(f);
  };

  const reset = () => {
    setFile(null);
    setRole("");
    setName("");
    setEmail("");
  };

  const onContinue = async () => {
    try {
      setLoading(true);

      // Read file content if present (for simplicity, we'll just send text or skip for now)
      // In a real app, we'd upload this file or extract text. 
      // For this demo, we'll extract text if it's text, or just pass context.
      // Since new_backend expects a string for resume, we'll omit it or send a placeholder.
      let resumeText = "";
      if (file) {
        // Placeholder for resume text extraction
        resumeText = `Resume for ${file.name}`;
      }

      const { data: { session } } = await supabase.auth.getSession();
      const userId = session?.user?.id || null;

      const response = await api.scheduleInterview({
        candidateName: name || "Candidate",
        candidateEmail: email || "candidate@example.com",
        role: role || "Software Engineer",
        resume: resumeText,
        userId: userId,
        interviewType: "Technical"
      });

      if (response.success && response.interviewId) {
        toast.success("Interview scheduled!");
        router.push(`/interview/${response.interviewId}`);
      } else {
        toast.error("Failed to schedule interview");
      }

    } catch (error: any) {
      toast.error(error.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const fileInfo = file
    ? `${file.name} • ${(file.size / 1024 / 1024).toFixed(2)} MB`
    : "No file selected";

  return (
    <Dialog>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-lg font-sans bg-black/50 backdrop-blur-xl border border-zinc-700/50 text-zinc-100 shadow-xl">
        <DialogHeader>
          <DialogTitle>Start New Interview</DialogTitle>
          <DialogDescription>
            Upload your resume and provide details to customize your interview session.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input id="name" placeholder="John Doe" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" placeholder="john@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="role">Target Role</Label>
            <Input
              id="role"
              placeholder="e.g., Senior Frontend Engineer"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            />
          </div>

          <div
            onDrop={onDrop}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-6 text-center transition-colors
                ${dragging ? "border-emerald-500 bg-emerald-500/10" : "border-zinc-700/60 hover:border-zinc-600"}
            `}
            onClick={onBrowseClick}
            role="button"
            tabIndex={0}
          >
            <Upload className="h-6 w-6 mb-2 opacity-90" />
            <p className="text-sm text-zinc-300">
              Resumes (PDF/DOC)
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={onFileChange}
              className="hidden"
            />
          </div>
          <div className="flex items-center gap-2 text-xs text-zinc-400">
            <FileText className="h-3 w-3" />
            <span>{fileInfo}</span>
            {file && <X className="h-3 w-3 cursor-pointer hover:text-white" onClick={() => setFile(null)} />}
          </div>
        </div>


        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" onClick={reset}>Cancel</Button>
          </DialogClose>
          <Button
            className="bg-emerald-600 hover:bg-emerald-500"
            onClick={onContinue}
            disabled={loading}
          >
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Start Interview
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
