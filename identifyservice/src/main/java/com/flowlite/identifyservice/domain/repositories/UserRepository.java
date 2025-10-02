package com.flowlite.identifyservice.domain.repositories;

import com.flowlite.identifyservice.domain.entities.User;
import java.util.Optional;
import java.util.UUID;


public interface UserRepository {

    Optional<User> findById(UUID id);
    Optional<User> findByUsername(String username);
    Optional<User> findByEmail(String email);
    User save(User user);
}
