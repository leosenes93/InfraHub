import type { UserRole } from "@/api/auth";

export function canWriteAssets(role: UserRole | undefined): boolean {
  return role === "admin" || role === "analyst" || role === "operator";
}

export function canDeleteAssets(role: UserRole | undefined): boolean {
  return role === "admin";
}
