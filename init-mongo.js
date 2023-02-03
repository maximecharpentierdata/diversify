db.createUser(
    {
        user: "diversify",
        pwd: "psswd",
        roles: [
            {
                role: "readWrite",
                db: "diversify"
            }
        ]
    }
)