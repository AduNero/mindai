import { ChangeEvent, FormEvent, useEffect, useState } from "react";

import { usersApi } from "@/api";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useToast } from "@/context/ToastContext";
import type { Profile } from "@/types";
import { extractErrorMessage } from "@/utils/errors";

export default function ProfilePage() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    usersApi
      .getMyProfile()
      .then(({ data }) => setProfile(data))
      .finally(() => setLoading(false));
  }, []);

  const update = (field: keyof Profile) => (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setProfile((p) => (p ? { ...p, [field]: e.target.value } : p));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!profile) return;
    setSaving(true);
    try {
      const { data } = await usersApi.updateMyProfile({
        bio: profile.bio,
        date_of_birth: profile.date_of_birth,
        gender: profile.gender,
        phone_number: profile.phone_number,
        country_code: profile.country_code,
        timezone: profile.timezone,
        emergency_contact_name: profile.emergency_contact_name,
        emergency_contact_phone: profile.emergency_contact_phone,
      });
      setProfile(data);
      showToast("Profile updated.", "success");
    } catch (err) {
      showToast(extractErrorMessage(err, "Couldn't update your profile."), "error");
    } finally {
      setSaving(false);
    }
  };

  const handlePictureUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const { data } = await usersApi.uploadProfilePicture(file);
      setProfile(data);
      showToast("Profile picture updated.", "success");
    } catch (err) {
      showToast(extractErrorMessage(err, "Couldn't upload that image."), "error");
    } finally {
      setUploading(false);
    }
  };

  if (loading || !profile) return <FullPageSpinner />;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Profile</h1>

      <div className="card flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center overflow-hidden rounded-full bg-brand-100 text-xl font-semibold text-brand-700 dark:bg-brand-950 dark:text-brand-300">
          {profile.profile_picture ? (
            <img src={profile.profile_picture} alt="Profile" className="h-full w-full object-cover" />
          ) : (
            profile.user.first_name[0]
          )}
        </div>
        <div>
          <p className="font-medium text-gray-900 dark:text-gray-100">{profile.user.full_name}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">{profile.user.email}</p>
          <label className="mt-2 inline-block cursor-pointer text-xs font-medium text-brand-600 hover:underline">
            {uploading ? "Uploading..." : "Change photo"}
            <input type="file" accept="image/jpeg,image/png,image/webp" onChange={handlePictureUpload} className="hidden" />
          </label>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-4">
        <div>
          <label className="label">Bio</label>
          <textarea className="input" rows={3} value={profile.bio} onChange={update("bio")} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Date of birth</label>
            <input type="date" className="input" value={profile.date_of_birth ?? ""} onChange={update("date_of_birth")} />
          </div>
          <div>
            <label className="label">Gender</label>
            <select className="input" value={profile.gender} onChange={update("gender")}>
              <option value="">Prefer not to say</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="non_binary">Non-binary</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Phone number</label>
            <input className="input" value={profile.phone_number} onChange={update("phone_number")} />
          </div>
          <div>
            <label className="label">Country code (e.g. US, GH)</label>
            <input
              className="input uppercase"
              maxLength={2}
              value={profile.country_code}
              onChange={update("country_code")}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Emergency contact name</label>
            <input className="input" value={profile.emergency_contact_name} onChange={update("emergency_contact_name")} />
          </div>
          <div>
            <label className="label">Emergency contact phone</label>
            <input className="input" value={profile.emergency_contact_phone} onChange={update("emergency_contact_phone")} />
          </div>
        </div>
        <button type="submit" disabled={saving} className="btn-primary">
          {saving ? "Saving..." : "Save changes"}
        </button>
      </form>
    </div>
  );
}
