import { ReactNode } from "react"
const authlayout = ({children}:{children:ReactNode}) => {
  return (
    <div className="auth-layout">{children}</div>
  )
}

export default authlayout
