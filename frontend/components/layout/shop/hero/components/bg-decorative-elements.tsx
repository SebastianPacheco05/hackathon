
const BgDecorativeElements = () => {
  return (
    <div className="absolute inset-0 overflow-hidden">
      <div className="absolute -top-32 -right-24 w-80 h-80 bg-linear-to-br from-[#00B207]/18 to-[#7BC47F]/12 rounded-full blur-3xl animate-pulse" style={{ animationDuration: "8s" }} />
      <div className="absolute top-12 -left-20 w-64 h-64 bg-linear-to-br from-[#34A853]/14 to-[#00B207]/10 rounded-full blur-3xl animate-pulse" style={{ animationDuration: "6s", animationDelay: "0.8s" }} />
      <div className="absolute bottom-10 right-16 w-48 h-48 bg-linear-to-br from-[#7BC47F]/20 to-[#34A853]/14 rounded-full blur-2xl animate-pulse" style={{ animationDuration: "9s", animationDelay: "1.6s" }} />

      <div className="absolute top-1/4 left-1/4 w-3 h-3 bg-[#00B207]/40 rounded-full animate-bounce" style={{ animationDuration: "2.8s" }} />
      <div className="absolute top-2/3 right-1/3 w-2 h-2 bg-[#34A853]/35 rounded-full animate-bounce" style={{ animationDuration: "3.2s", animationDelay: "0.4s" }} />
      <div className="absolute bottom-1/4 left-1/2 w-2.5 h-2.5 bg-[#7BC47F]/40 rounded-full animate-pulse" style={{ animationDuration: "3.6s", animationDelay: "0.7s" }} />

      <div className="absolute inset-0 opacity-5">
        <div
          className="w-full h-full animate-pulse"
          style={{
            backgroundImage: `
              linear-gradient(rgba(0, 178, 7, 0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0, 178, 7, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: "56px 56px",
            animationDuration: "20s",
          }}
        />
      </div>
    </div>
  )
}

export default BgDecorativeElements