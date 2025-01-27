package org.example;
public class Main {
    public static void main(String[] args) {
   etudiant soadlabib=new etudiant("souad","labib",21);
   etudiant atanan=new etudiant("atanan","sasbo",22);


}}
class etudiant{
    public String nom;
    public String prenom;
    public int age;
    etudiant(String nom, String prenom, int age) {
        nom=this.nom;
        prenom=this.prenom;
        this.age=age;
    }
}