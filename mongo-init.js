db.createUser(
    {
        user: "diversify",
        pwd: "password",
        roles: [
            {
                role: "readWrite",
                db: "diversify"
            }
        ]
    }
);