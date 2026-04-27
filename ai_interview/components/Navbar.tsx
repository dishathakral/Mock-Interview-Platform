"use client"

import { useEffect, useState } from "react";
import Link from 'next/link';
import Image from 'next/image';
import { Button } from "@/components/ui/button";
import ResumeUploadDialog from '@/components/ResumeUploadDialog';
import { supabase } from "@/lib/supabase";
import { User } from "@supabase/supabase-js";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

const Navbar = () => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const getSession = async () => {
            const { data: { session } } = await supabase.auth.getSession();
            setUser(session?.user ?? null);
            setIsLoading(false);
        };

        getSession();

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            setUser(session?.user ?? null);
        });

        return () => subscription.unsubscribe();
    }, []);

    const handleSignOut = async () => {
        try {
            await supabase.auth.signOut();
            toast.success("Signed out successfully");
            router.refresh();
        } catch (error) {
            toast.error("Failed to sign out");
        }
    };

    return (
        <nav className="fixed inset-x-0 top-0 z-50 bg-black flex items-center justify-between px-8 py-5 shadow-md">
            <Link href='/' className='flex items-center gap-2'>
                <Image src="/logo.svg" alt="logo" width={38} height={32} style={{ height: 'auto' }} />
                <h2 className='text-primary-100'>HireReady</h2>
            </Link>

            <div className="flex items-center font-sans gap-4">
                <ResumeUploadDialog
                    trigger={
                        <Button className="cursor-pointer bg-emerald-600 hover:bg-emerald-500 text-white font-bold tracking-wide flex items-center gap-2">
                            Upload Resume
                        </Button>
                    } />

                {isLoading ? (
                    <div className="w-20 h-8 bg-gray-800 animate-pulse rounded ml-9"></div>
                ) : user ? (
                    <div className="flex items-center gap-4 ml-9">
                        <span className="text-white text-sm hidden sm:block">
                            Hi, {user.user_metadata?.full_name || user.email?.split('@')[0]}
                        </span>
                        <Button onClick={handleSignOut} variant="outline" className="text-white border-red-400 hover:bg-red-950 bg-transparent">
                            Sign Out
                        </Button>
                    </div>
                ) : (
                    <>
                        <Button asChild variant="outline" className="ml-9 text-white border-indigo-400 bg-transparent">
                            <Link href="/sign_in">Login</Link>
                        </Button>
                        <Button asChild className="bg-indigo-600 hover:bg-indigo-500 text-white">
                            <Link href="/sign_up">Register</Link>
                        </Button>
                    </>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
