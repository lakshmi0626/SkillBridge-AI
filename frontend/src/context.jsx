import React,{createContext,useContext,useState} from 'react';
const AuthContext=createContext(null);
export function AuthProvider({children}){const [user,setUser]=useState(()=>{try{return JSON.parse(localStorage.getItem('sb_user'))}catch{return null}});const login=(data)=>{localStorage.setItem('sb_token',data.access_token);localStorage.setItem('sb_user',JSON.stringify(data.user));setUser(data.user)};const logout=()=>{localStorage.removeItem('sb_token');localStorage.removeItem('sb_user');setUser(null)};return <AuthContext.Provider value={{user,login,logout}}>{children}</AuthContext.Provider>}
export const useAuth=()=>useContext(AuthContext);
