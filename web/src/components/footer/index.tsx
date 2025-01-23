import { Layout } from 'antd'
import styles from './index.module.less'

const { Footer } = Layout

const NavFooter = () => {
    return (
        <Footer className={styles.footer}>
            <div className={styles.content}>
                <div className={styles.copyright}>
                    Copyright © 2024 NMA. All Rights Reserved.
                </div>
                <div className={styles.links}>
                    <a href="#">关于我们</a>
                    <span className={styles.divider}>|</span>
                    <a href="#">联系我们</a>
                    <span className={styles.divider}>|</span>
                    <a href="#">隐私政策</a>
                </div>
            </div>
        </Footer>
    )
}

export default NavFooter
