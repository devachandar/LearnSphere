/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1E1B4B",
        plum: "#4C1D95",
        coral: "#F97362",
        paper: "#FAF9FC",
        line: "#E4E1EF",
        slate: "#5B5570",
      },
      fontFamily: {
        display: ["Sora", "sans-serif"],
        body: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
