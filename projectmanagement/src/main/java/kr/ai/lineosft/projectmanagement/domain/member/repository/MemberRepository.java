package kr.ai.lineosft.projectmanagement.domain.member.repository;

import kr.ai.lineosft.projectmanagement.domain.member.entity.Member;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface MemberRepository extends JpaRepository<Member, Long> {
    Optional<Member> findByEmail(String email);
    boolean existsByEmail(String email);
    Optional<Member> findByNicknameAndPhoneNumber(String nickname, String phoneNumber);
    Optional<Member> findByEmailAndNicknameAndPhoneNumber(String email, String nickname, String phoneNumber);
}
