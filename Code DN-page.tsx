"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { GitBranch, User, LogOut, Plus } from "lucide-react";

interface User {
  id: string;
  username: string;
  email: string;
  avatarUrl?: string;
  bio?: string;
}

interface Repository {
  id: string;
  name: string;
  description: string;
  isPublic: boolean;
  language: string;
  starsCount: number;
  forksCount: number;
  updatedAt: string;
}

function UserRepositories({ userId }: { userId: string }) {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRepositories();
  }, [userId]);

  const fetchRepositories = async () => {
    try {
      const response = await fetch(`/api/repositories?userId=${userId}`);
      if (response.ok) {
        const data = await response.json();
        setRepositories(data.repositories);
      }
    } catch (error) {
      console.error("Failed to fetch repositories:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-muted-foreground">Loading repositories...</div>;
  }

  if (repositories.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-muted-foreground py-8">
            <p className="mb-4">You haven't created any repositories yet.</p>
            <Link href="/new">
              <Button>Create your first repository</Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-4">
      {repositories.map((repo) => (
        <Card key={repo.id}>
          <CardContent className="pt-6">
            <Link href={`/repositories/${repo.id}`}>
              <h3 className="text-lg font-semibold text-primary hover:underline mb-2">
                {repo.name}
              </h3>
            </Link>
            <p className="text-sm text-muted-foreground mb-4">{repo.description}</p>
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <span className={`w-3 h-3 rounded-full ${getLanguageColor(repo.language)}`} />
                {repo.language}
              </span>
              <span>Updated {formatDate(repo.updatedAt)}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function getLanguageColor(language: string): string {
  const colors: Record<string, string> = {
    TypeScript: "bg-blue-500",
    JavaScript: "bg-yellow-500",
    Python: "bg-blue-400",
    Java: "bg-orange-500",
    Go: "bg-cyan-500",
    Rust: "bg-orange-600",
    C: "bg-gray-500",
    "C++": "bg-blue-600",
  };
  return colors[language] || "bg-gray-400";
}

function formatDate(dateStr: string | Date): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days === 0) return "today";
  if (days === 1) return "yesterday";
  if (days < 7) return `${days} days ago`;
  if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
  return `${Math.floor(days / 30)} months ago`;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await fetch("/api/auth/me");
      if (!response.ok) {
        router.push("/login");
        return;
      }
      const data = await response.json();
      setUser(data.user);
    } catch (error) {
      console.error("Auth check failed:", error);
      router.push("/login");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch("/api/auth/logout", { method: "POST" });
      router.push("/");
      router.refresh();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <GitBranch className="h-6 w-6" />
            <span className="text-xl font-bold">CodeHub</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href={`/users/${user?.username}`}>
              <Button variant="ghost" size="icon">
                <User className="h-5 w-5" />
              </Button>
            </Link>
            <Button variant="ghost" size="icon" onClick={handleLogout}>
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">
            Welcome, {user?.username}!
          </h1>
          <p className="text-muted-foreground">
            Manage your repositories and collaborate with the community
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                New Repository
              </CardTitle>
              <CardDescription>
                Create a new repository to start your project
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/new">
                <Button className="w-full">Create Repository</Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Explore Repositories</CardTitle>
              <CardDescription>Discover repositories from the community</CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/explore">
                <Button variant="outline" className="w-full">Explore</Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>My Profile</CardTitle>
              <CardDescription>View and edit your profile</CardDescription>
            </CardHeader>
            <CardContent>
              <Link href={`/users/${user?.username}`}>
                <Button variant="outline" className="w-full">View Profile</Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* User's Repositories */}
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">My Repositories</h2>
          <UserRepositories userId={user?.id || ""} />
        </div>
      </main>
    </div>
  );
}
