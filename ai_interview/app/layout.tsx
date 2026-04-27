import type { Metadata } from "next";
import {Mona_Sans} from "next/font/google";
import "./globals.css";
import { Toaster } from "sonner";

const monaSans = Mona_Sans({
  variable: "--font-mona-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "HireReady",
  description: "Ace Every Question, Own Every Interview",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${monaSans.className} antialiased pattern-bg`}
        style={{ backgroundImage: "var(--bg-pattern)" }}
      >
        {/* <video
          className="absolute top-0 left-0 w-full h-full object-cover -z-10"
          autoPlay
          loop
          muted
          playsInline
        >
          <source src="/10296173-hd_1920_1080_25fps.mp4" type="video/mp4" />
        </video> */}
        {children}
        <Toaster />
      </body>
    </html>
  );
}
