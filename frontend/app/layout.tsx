import "./globals.css";

export const metadata = { title: "SQL Lab", description: "Run and inspect PostgreSQL scenarios from beginner to professional" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
